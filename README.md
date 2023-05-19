### 第一交易
#### 模块划分
    1. 策略模块 (开发中) robot/model
    2. 交易模块 (开发中) robot/deal
    3. 回测模块 (开发中) robot/back_test
    4. 后端模块 (开发中) apps/trading
    5. 通知模块 (开发中) ...
    6. 配置模块 (待开发) ...
#### 当前策略
    1. 2B 突破策略 robot/model/TOWB.py
```yaml
symbol =  [
        'XRP/USDT',
        'BTC/USDT',
        'ATOM/USDT',
        'BCH/USDT',
        'RSR/USDT',
        'LUNC/USDT',
        'STG/USDT',
        'ETH/USDT',
        'EOS/USDT',
        'ADA/USDT',
        'RVN/USDT',
        'ETC/USDT',
        'DOGE/USDT',
    ]
合约回测，不带杠杆
30m周期
样本数量=644,胜率=54.81%
平均利润=0.4233%
利润中位数=0.3904%
胜者组平均利润=2.1202%
败者组平均利润=-1.6351%
平均盈亏比=0.4403%
平均持仓k线=9.1584

15m 周期
样本数量=452,胜率=59.29%
平均利润=0.7109%
利润中位数=0.8732%
胜者组平均利润=2.1359%
败者组平均利润=-1.3648%
平均盈亏比=0.8162%
平均持仓k线=9.5177



```
