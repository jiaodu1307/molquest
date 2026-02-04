```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 e9f0b9a7-95d5-423d-bf7d-d8ffaf16bde5 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C7H5N'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 103.04219916}]
node_2 --> node_3
node_4[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR')}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ 7.68-7.67 (d, J = 8.3 Hz, 2 H), 7.64-7.61 ...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (125 MHz, CDCl3) δ 132.80, 132.17, 129.15, 118.87, 112.46'}]
node_6 --> node_7
node_8[AI: {'type': 'text', 'text': '根据已获取的分析数据，推断如下：\n\n1. **分子式与不饱和度**：\n * 分子式为 **C7H5N*...]
node_7 --> node_8
```