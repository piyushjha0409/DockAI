from tortoise import Tortoise

async def init_db():
    await Tortoise.init(
        db_url="postgres://neondb_owner:npg_qmRtEr6B3kVU@ep-shiny-dust-a5q78l7c-pooler.us-east-2.aws.neon.tech/neondb",
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()
