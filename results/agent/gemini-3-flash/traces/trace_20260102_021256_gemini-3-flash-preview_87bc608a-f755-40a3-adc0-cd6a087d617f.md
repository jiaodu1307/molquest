```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 87bc608a-f755-40a3-adc0-cd6a087d617f 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Check_Data, Calculate_DBE]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C13H21N'}]
node_1 --> node_2
node_3[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_M...]
node_2 --> node_3
node_4[Tool: Calculate_DBE (success): {'result': 4.0}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1 H NMR (300 MHz, CD2Cl2): δ = 7.43 (s_br, 1H), 5.57 (d, J = 2.9 Hz,...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (75 MHz, CD2Cl2): δ = 133.7, 128.6, 121.2, 106.2, 34.6, 32.6...]
node_6 --> node_7
node_8[AI: {'type': 'text', 'text': '结合分子式 $C_{13}H_{21}N$ 和不饱和度 $DBE=4$ 进行分析。在 $^{13}C\\ N...]
node_7 --> node_8
node_9[AI: {'type': 'text', 'text': '根据提供的波谱数据和分子信息，对编号为 87bc608a-f755-40a3-adc0-cd6a087d61...]
node_8 --> node_9
```