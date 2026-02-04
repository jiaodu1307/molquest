import json
import argparse
import sys
import os
from typing import Dict, Any, Optional

try:
    from rdkit import Chem
    from rdkit import RDLogger
    from rdkit import DataStructs
    from rdkit.Chem import AllChem, Draw
    # Silence RDKit warnings/errors
    RDLogger.DisableLog('rdApp.*')
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("Warning: RDKit not found. SMILES comparison will be exact string matching only.", file=sys.stderr)

def canonicalize_smiles(smiles: str) -> Optional[str]:
    """
    Canonicalize a SMILES string using RDKit.
    Returns None if RDKit is unavailable or parsing fails.
    """
    if not RDKIT_AVAILABLE:
        return smiles.strip() if smiles else None # Fallback
    
    if not smiles:
        return None

    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
    except Exception:
        return None

def calculate_similarity(smiles1: str, smiles2: str) -> float:
    """
    Calculate Tanimoto similarity between two SMILES strings using Morgan fingerprints.
    Returns 0.0 if RDKit is unavailable or parsing fails.
    """
    if not RDKIT_AVAILABLE or not smiles1 or not smiles2:
        return 0.0

    try:
        mol1 = Chem.MolFromSmiles(smiles1)
        mol2 = Chem.MolFromSmiles(smiles2)
        if mol1 is None or mol2 is None:
            return 0.0
        
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
        
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except Exception:
        return 0.0

def save_structure_image(smiles: str, filepath: str) -> bool:
    """
    Generate and save a 2D structure image for a SMILES string.
    Returns True if successful, False otherwise.
    """
    if not RDKIT_AVAILABLE or not smiles:
        return False
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            Draw.MolToFile(mol, filepath, size=(300, 300))
            return True
    except Exception:
        pass
    return False

def evaluate(predictions_path: str, ground_truth_path: str, output_md: Optional[str] = None, visualize: bool = False, images_dir: str = "evaluation_images", output_json: Optional[str] = None):
    print(f"Loading predictions from: {predictions_path}")
    with open(predictions_path, 'r', encoding='utf-8') as f:
        predictions_data = json.load(f)

    print(f"Loading ground truth from: {ground_truth_path}")
    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        ground_truth_data = json.load(f)

    # Index ground truth by UUID
    ground_truth_map: Dict[str, Dict[str, Any]] = {
        item['uuid']: item for item in ground_truth_data
    }

    total = 0
    correct = 0
    valid_predictions = 0
    missing_ground_truth = 0
    parsing_errors = 0
    total_similarity = 0.0
    total_confidence = 0.0
    
    results = []

    print("-" * 128)
    print(f"{'UUID':<38} | {'Match':<5} | {'Sim':<4} | {'Conf':<4} | {'Pred (Canonical)':<25} | {'True (Canonical)':<25}")
    print("-" * 128)

    for pred_item in predictions_data:
        uuid = pred_item.get('uuid')
        if not uuid:
            continue
            
        final_result = pred_item.get('final_result', {})
        predicted_smiles = final_result.get('predicted_smiles')
        confidence = final_result.get('confidence', 0.0)
        
        if uuid not in ground_truth_map:
            missing_ground_truth += 1
            continue
            
        total += 1
        total_confidence += confidence
        gt_item = ground_truth_map[uuid]
        true_smiles = gt_item.get('smiles')
        
        # Canonicalize
        canon_pred = canonicalize_smiles(predicted_smiles) if predicted_smiles else None
        canon_true = canonicalize_smiles(true_smiles) if true_smiles else None
        
        # Check validity
        is_valid = (canon_pred is not None)
        if is_valid:
            valid_predictions += 1
        else:
             if predicted_smiles: # Only count as parsing error if something was actually predicted
                 parsing_errors += 1
        
        # Calculate similarity
        similarity = 0.0
        if is_valid and canon_true:
            similarity = calculate_similarity(canon_pred, canon_true)
            total_similarity += similarity

        is_match = False
        if RDKIT_AVAILABLE:
            if canon_pred and canon_true:
                is_match = (canon_pred == canon_true)
        else:
             # Fallback exact match
             if predicted_smiles and true_smiles:
                 is_match = (predicted_smiles.strip() == true_smiles.strip())
                 # For string match, similarity is 1.0 or 0.0
                 similarity = 1.0 if is_match else 0.0
                 if is_match: total_similarity += 1.0
        
        if is_match:
            correct += 1
            
        results.append({
            "uuid": uuid,
            "match": is_match,
            "valid": is_valid,
            "similarity": similarity,
            "confidence": confidence,
            "predicted": predicted_smiles,
            "true": true_smiles,
            "canon_predicted": canon_pred,
            "canon_true": canon_true
        })
        
        # Print output for log
        p_display = canon_pred if canon_pred else (predicted_smiles if predicted_smiles else "N/A")
        t_display = canon_true if canon_true else (true_smiles if true_smiles else "N/A")
        
        # Truncate for display
        p_short = (p_display[:23] + '..') if len(p_display) > 25 else p_display
        t_short = (t_display[:23] + '..') if len(t_display) > 25 else t_display
        
        match_str = "YES" if is_match else "NO"
        sim_str = f"{similarity:.2f}"
        conf_str = f"{confidence:.2f}"
        print(f"{uuid:<38} | {match_str:<5} | {sim_str:<4} | {conf_str:<4} | {str(p_short):<25} | {str(t_short):<25}")

    print("-" * 128)
    
    accuracy = (correct / total * 100) if total > 0 else 0
    validity_rate = (valid_predictions / total * 100) if total > 0 else 0
    avg_similarity = (total_similarity / valid_predictions) if valid_predictions > 0 else 0.0
    avg_confidence = (total_confidence / total) if total > 0 else 0.0
    
    print(f"\nEvaluation Complete:")
    print(f"Total evaluated: {total}")
    print(f"Valid Predictions: {valid_predictions} ({validity_rate:.2f}%)")
    print(f"Correct Matches: {correct} ({accuracy:.2f}%)")
    print(f"Average Similarity (Tanimoto): {avg_similarity:.4f}")
    print(f"Average Confidence: {avg_confidence:.4f}")
    
    if parsing_errors > 0:
        print(f"SMILES Parsing Errors (Invalid predictions): {parsing_errors}")
    if missing_ground_truth > 0:
        print(f"Items missing in ground truth: {missing_ground_truth}")

    if not RDKIT_AVAILABLE:
        print("\nNOTE: RDKit was not available. Comparison was done using raw string matching.")
        print("For accurate chemical comparison, please install rdkit: pip install rdkit")

    if output_md:
        if visualize and RDKIT_AVAILABLE:
            if not os.path.exists(images_dir):
                try:
                    os.makedirs(images_dir)
                    print(f"Created directory for images: {images_dir}")
                except OSError as e:
                    print(f"Error creating images directory: {e}", file=sys.stderr)
                    visualize = False # Disable if cannot create dir

        with open(output_md, "w", encoding="utf-8") as f:
            f.write(f"# SMILES Prediction Evaluation\n\n")
            f.write(f"- **Predictions File**: `{predictions_path}`\n")
            f.write(f"- **Ground Truth File**: `{ground_truth_path}`\n")
            f.write(f"- **Accuracy**: {accuracy:.2f}% ({correct}/{total})\n")
            f.write(f"- **Validity Rate**: {validity_rate:.2f}% ({valid_predictions}/{total})\n")
            f.write(f"- **Average Similarity**: {avg_similarity:.4f}\n")
            f.write(f"- **Average Confidence**: {avg_confidence:.4f}\n")
            
            if not RDKIT_AVAILABLE:
                f.write("- **Note**: RDKit not available, using string matching.\n")
            if parsing_errors > 0:
                f.write(f"- **Parsing Errors**: {parsing_errors}\n")
            
            f.write("\n## Detailed Results\n\n")
            
            if visualize and RDKIT_AVAILABLE:
                f.write("| UUID | Match | Sim | Conf | Valid | Predicted Structure | True Structure | Raw Predicted |\n")
            else:
                f.write("| UUID | Match | Sim | Conf | Valid | Predicted (Canonical) | True (Canonical) | Raw Predicted |\n")
            
            f.write("|---|---|---|---|---|---|---|---|\n")
            
            for res in results:
                uuid = res['uuid']
                match_icon = "✅" if res['match'] else "❌"
                valid_icon = "✅" if res['valid'] else "❌"
                similarity = f"{res['similarity']:.2f}"
                confidence = f"{res['confidence']:.2f}"
                
                p_display = "*N/A*"
                t_display = "*N/A*"

                if visualize and RDKIT_AVAILABLE:
                    # Generate images
                    pred_filename = f"{uuid}_pred.png"
                    true_filename = f"{uuid}_true.png"
                    pred_path = os.path.join(images_dir, pred_filename)
                    true_path = os.path.join(images_dir, true_filename)
                    
                    # Use canonical smiles if available, otherwise raw for generation attempt
                    s_pred = res['canon_predicted'] if res['canon_predicted'] else res['predicted']
                    s_true = res['canon_true'] if res['canon_true'] else res['true']
                    
                    has_p_img = save_structure_image(s_pred, pred_path)
                    has_t_img = save_structure_image(s_true, true_path)
                    
                    # For markdown, we need relative path from the md file location
                    # Assuming md file and images_dir are relative to current CWD or related
                    # Simple approach: use the path provided in images_dir
                    
                    p_display = f"![Pred]({pred_path})" if has_p_img else "*Invalid*"
                    t_display = f"![True]({true_path})" if has_t_img else "*Invalid*"
                else:
                    # Format code blocks for SMILES to prevent markdown formatting issues
                    p_display = f"`{res['canon_predicted']}`" if res['canon_predicted'] else "*N/A*"
                    t_display = f"`{res['canon_true']}`" if res['canon_true'] else "*N/A*"

                p_raw = f"`{res['predicted']}`" if res['predicted'] else "*N/A*"
                
                f.write(f"| {uuid} | {match_icon} | {similarity} | {confidence} | {valid_icon} | {p_display} | {t_display} | {p_raw} |\n")
        
        print(f"\nMarkdown report saved to: {output_md}")
        if visualize and RDKIT_AVAILABLE:
            print(f"Structure images saved to: {images_dir}")

    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Evaluation results saved to JSON: {output_json}")

    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Evaluation results saved to JSON: {output_json}")

    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Evaluation results saved to JSON: {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SMILES predictions.")
    parser.add_argument("--predictions", default="results/claude-sonnet-4_5/claude-sonnet-4_5merged_runs.json", help="Path to the predictions JSON file")
    parser.add_argument("--ground_truth", default="data/processed/molecules_version_3_0113.json", help="Path to the ground truth JSON file")
    parser.add_argument("--output-md", default="claude-sonnet-4_5_evaluation_report.md", help="Path to save the markdown report")
    parser.add_argument("--output-json", default=None, help="Path to save the evaluation results in JSON format")
    parser.add_argument("--visualize", action="store_true", help="Generate molecular structure images in markdown report")
    parser.add_argument("--images-dir", default="claude-sonnet-4_5_evaluation_images", help="Directory to save generated images")
    
    args = parser.parse_args()
    
    evaluate(args.predictions, args.ground_truth, args.output_md, args.visualize, args.images_dir, args.output_json)