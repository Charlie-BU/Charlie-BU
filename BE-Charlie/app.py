from robyn import Robyn, ALLOW_CORS

from subRouters.api import apiRouter

app = Robyn(__file__)
app.include_router(apiRouter)
# 生产环境需要注释：使用nginx解决跨域
ALLOW_CORS(app, origins=["http://localhost:5173"])


@app.get("/")
async def index():
    return "Welcome to Charlie's Backend"


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=1209)
