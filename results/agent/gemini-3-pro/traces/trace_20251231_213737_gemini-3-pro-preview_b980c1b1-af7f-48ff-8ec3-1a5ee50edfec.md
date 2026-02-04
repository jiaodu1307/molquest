```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 b980c1b1-af7f-48ff-8ec3-1a5ee50edfec 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C14H10ClNO2'}]
node_1 --> node_2
node_3[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_2 --> node_3
node_4[AI: Call Get_1H_NMR, Get_13C_NMR]
node_3 --> node_4
node_5[Tool: Get_1H_NMR (success): {'result': 'd 8.23 (d, J = 8.8 Hz, 2H), 7.63 (d, J = 8.8 Hz, 2H), 7.48 (d, J = 8...]
node_4 --> node_5
node_6[Tool: Get_13C_NMR (success): {'result': 'd 146.9, 143.5, 134.7, 134.6, 131.9, 129.1, 128.2, 126.9, 126.9, 124...]
node_5 --> node_6
node_7[AI: {'type': 'text', 'text': '自然语言分析：\n1. **分子式与不饱和度**：\n * 通过 `Measure_Formula` 得到分...]
node_6 --> node_7
```