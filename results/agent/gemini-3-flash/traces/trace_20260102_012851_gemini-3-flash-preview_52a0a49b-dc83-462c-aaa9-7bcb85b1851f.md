```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 52a0a49b-dc83-462c-aaa9-7bcb85b1851f 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C20H21NO3S'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 355.124214532}]
node_2 --> node_3
node_4[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (400 MHz, CDCl3): δ 7.73 (dt, J = 6.9, 1.8 Hz, 1H), 7.62 – 7....]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (101 MHz, CDCl3): δ 153.69, 140.74, 134.85, 133.48, 132.42, ...]
node_6 --> node_7
node_8[AI: Call Get_IR]
node_7 --> node_8
node_9[Tool: Get_IR (error): {'error': 'Sample 52a0a49b-dc83-462c-aaa9-7bcb85b1851f has no 'ir' data.'}]
node_8 --> node_9
node_10[AI: Call Get_HRMS]
node_9 --> node_10
node_11[Tool: Get_HRMS (success): {'result': 'HRMS (ESI+): m/z calc’d for C20H21NO3SNa (M+Na)+: 378.1135, found: 3...]
node_10 --> node_11
node_12[AI: Call Get_Melting_Point]
node_11 --> node_12
node_13[Tool: Get_Melting_Point (success): {'result': '85.8 – 87.7 °C'}]
node_12 --> node_13
node_14[AI: {'type': 'text', 'text': '根据对样品 52a0a49b-dc83-462c-aaa9-7bcb85b1851f 的系统分析，推断其结构...]
node_13 --> node_14
node_15[AI: {'type': 'text', 'text': '根据谱学数据分析，该化合物的分子式为 $C_{20}H_{21}NO_3S$，不饱和度（DBE）为 11。H...]
node_14 --> node_15
```