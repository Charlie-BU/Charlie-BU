## 探索 MCP 协议及其应用场景

::: primary
AI app 发展如火如荼的今天，MCP 横空出世。就技术架构层面来说，MCP 是一套协议、一个标准，它与 AI 本质上并无关系，但 MCP 的存在，利用其能力极大地扩展了现有LLM（或是AI Agent）的能力，让它们在面对自身解决不了的问题时，通过一套统一的标准进行外部工具的调用。
:::

### 什么是 MCP

在不同的场景内，MCP可以有成千上万的定义。在 [MCP官网](https://modelcontextprotocol.io/docs/getting-started/intro) 中，MCP是这样被定义的：

> MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems.

举例如下：

> Using MCP, AI applications like Claude or ChatGPT can connect to data sources (e.g. local files, databases), tools (e.g. search engines, calculators) and workflows (e.g. specialized prompts)—enabling them to access key information and perform tasks.

而在袁进老师的MCP的介绍课程中，他进行了如下定义：

> MCP (Model Context Protocol)，模型上下文协议。其旨在为AI与外部程序之间建立通信标准，从而使得外部程序可以被部署到任意AI，也使得AI应用可以使用任意的外部程序。

以上，是我认为最贴切，以及与本文关联度最高的定义性文字。

### 技术层面：实现细节

#### 一些术语

| 术语                          | 定义                                                  | 在 MCP 中的作用                    | 类比/备注         |
| :---------------------------: | :---------------------------------------------------: | :-----------------------------: | :-------------: |
| **MCP Host**                | MCP 的运行环境，通常是 AI 应用本身（如 ChatGPT、Claude、开源 Agent 框架） | 提供上下文，发起请求                    | 浏览器           |
| **MCP Client**              | Host 中负责和 Server 通信的部分                              | 将模型的需求转换成 MCP 请求，发送给 Server   | HTTP Client   |
| **MCP Server**              | 按 MCP 协议暴露功能的外部程序/服务                                | 提供工具和资源                       | Web Server    |
| **MCP Tool**         | MCP Server 提供的具体功能接口                                | 供模型调用，例如 `search_docs(query)` | API Endpoint  |
| **Tool Call**               | Host/Client 发起对某个 MCP Tool 的调用动作                    | 模型通过 JSON-RPC 请求调用外部功能        | API 调用        |
| **MCP Resource** | Server 提供的静态/动态资源                                   | 如数据库表、文件目录、知识库                | REST API 中的资源 |
| **Session**                 | Client 与 Server 之间的一次会话上下文                          | 保存连接状态，直到关闭                   | 登录 Session    |
| **Schema**                  | 描述工具参数、返回值的数据结构（JSON Schema）                        | 确保调用和响应符合标准                   | API 文档中的参数定义  |
| **JSON-RPC**                  | 一种基于 JSON 的远程过程调用协议 | MCP 底层消息格式标准                   | gRPC 的轻量替代  |

#### MCP Client 与 MCP Server 的通信方式

- stdio：标准输入输出流，通常只在Client和Server都在本地时使用。高效而简洁，更常用
- http：可本地、可远程通信

#### 通信格式

基于`JSON-RPC`的进一步规范

> JSON-RPC 是一种基于 JSON 格式的远程过程调用（Remote Procedure Call, RPC）协议。有以下特点：
>
> - 轻量级：只依赖 JSON，没有复杂的规范。
> - 与语言无关：只要能处理 JSON，就能实现。
> - 点对点调用：一方发请求（调用某方法），另一方返回结果。

#### 基本规范

##### 初始化 initialize

**request** (Client -> Server)

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {"listChanged": true},
            "sampling": {},
            "elicitation": {},
        },
        "clientInfo": {
            "name": "ExampleClient",
            "title": "Example Client Display Name",
            "version": "1.0.0",
        },
    },
}
```

**response** (Server -> Client)

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "serverInfo": {
            "name": "ExampleServer",
            "title": "Example Server Display Name",
            "version": "1.0.0",
        },
        "capabilities": {"tools": true, "resources": true, "sampling": false},
    },
}
```

说明：
- id：必须和请求一致，用来对应请求/响应
- serverInfo：告知客户端服务端的信息（名称、标题、版本号）
- capabilities：表明服务端支持的能力，比如：
    - tools: 是否提供可调用工具
    - resources: 是否暴露资源（文件、数据库等）
    - sampling: 是否支持采样相关功能

##### 工具发现 tools/list

Client发起请求，Server响应服务器有哪些tools可供Client调用

**request** (Client -> Server)

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}
```

**response** (Server -> Client) 

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "tools": [
            {
                "name": "get_weather",
                "title": "Weather Information Provider",
                "description": "Get current weather information for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or zip code",
                        }
                    },
                    "required": ["location"],
                },
            }
        ]
    },
}
```

##### 工具调用 tools/call

**request** (Client -> Server)

```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get_weather",
        "arguments": {
            "location": "Shanghai"
        }
    }
}
```

**response** (Server -> Client) 

```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        // tools执行结果放到content中；可能有多个结果，所以是数组
        "content": [{
            "type": "text",
            "text": "72℉"
        }]
    }
}
```

除了`text`外，`tools/call`还可能返回其他的数据类型，具体见[官方文档](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#tool-result)。

#### MCP SDK

> 本文仅做 Node 环境下 MCP SDK 介绍，其他环境下 SDK（如 Python 等）请自行查阅

借助官方的`@modelcontextprotocol/sdk`，可以非常方便地开发MCP Server。

1. 首先，安装SDK

    ```bash
    npm install @modelcontextprotocol/sdk
    // 或
    pnpm add @modelcontextprotocol/sdk
    ```

2. new一个Server实例

    `server.js`

    ```javascript
    import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

    const server = new Server({
        name: "Charlie's MCP Server",
        title: "Charlie's MCP Server",
        version: "0.1.0"
    })
    ```

3. 选择通信方式、建立通信信道

    `server.js`

    ```javascript
    import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

    const transport = new StdioServerTransport();
    ```


4. 注册MCP Tools

    `server.js`

    ```javascript
    import { z } from 'zod';
    import fs from 'fs';

    server.registerTool(
        "sum",      // 函数名
        {
            title: "两数求和",
            descriotion: "得到两个数的和",
            inputSchema: {
                a: z.number().describe("第一个数"),
                b: z.number().describe("第二个数"),
            }
        },
        ({a, b}) => {
            return {
                content: [      // 函数执行结果可能不止一个，用数组
                    {
                        type: "text",
                        text: `两数的和为: ${a + b}`
                    }
                ]
            }
        }
    )
    ```

5. 连接服务器

    `server.js`

    ```javascript
    server.connect(transport)
    ```

### 功能层面：应用场景

#### 对接 AI 应用程序

> AI 应用程序：与大模型交互等应用程序。如 ChatGPT、Claude Desktop、Cursor、Trae 等

当大模型理解用户问题时，若用户的需求超过的大模型的能力范围，或是存在与大模型连接的MCP Tool能够更好地解决该问题，大模型会先判断选择适合的MCP Tool，再进行Tool Call。从而极大扩展了大模型的能力。

原理图如下：

![mcp-ai-app](https://charlie-assets.oss-rg-china-mainland.aliyuncs.com/images/mcp-ai-app.png?x-oss-process=image/resize,w_800)

那么，对于一个具备MCP能力的AI应用程序的架构，如图所示：

![mcp-infra](https://charlie-assets.oss-rg-china-mainland.aliyuncs.com/images/mcp-infra.png?x-oss-process=image/resize,w_800)

以上，MCP的技术和一般场景便介绍差不多了。自然它的功能远不止于Tool Call，具体情境下的具体功能实现还得继续参考官方文档。感谢阅读。
