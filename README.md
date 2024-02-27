# ComfyUI-Dist
For distributed processing ComfyUI workflows within a local area network

---
BETA:
- 因为搞不起大显卡，同时局域网内有多台闲置的小显存的显卡机器，因此想到要写个这个custom_nodes模块
- 本repo大量参考了https://github.com/city96/ComfyUI_NetDist的源码，但是这个repo我感觉用起来还是不够友好，以及有些必要的功能没有，在他的代码基础上改有点不够效率，反正python重写都是很快的
- 先用中文记下来，开发完了后会补上英文的README
- 我个人对这个模块的功能计划：

| 序号 | 计划 |
| --- | --- |
| 1 | 入参：能够LoadAnythingFromURL |
| 2 | 入参：能够LoadAnythingFromLocalStorage |
| 3 | 准备一个最低依赖的ComfyUI的版本（源码、docker镜像）能够在NAS这种最简陋的linux系统上跑起来，仅具备上传接口的功能 |
| 4 | 重构ComfyUI_NetDist的节点的逻辑，使它更直观更好用 |
| 5 | 写一个转换的脚本，能够从普通工作流转换为分布式的工作流 |

P.S.
1. 我不会js，跟ComfyUI前端界面有关的都写不了，得排后面
2. 欢迎在issues里提需求，Be free to open an issue to propose requirements.
3. 欢迎点个watch或者star什么的push我写
