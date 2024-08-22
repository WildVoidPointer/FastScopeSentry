from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
import json


class SparkAiModel:
    SPARKAI_URL = 'wss://spark-api.xf-yun.com/v1.1/chat'

    SPARKAI_APP_ID = '597fe6fd'
    SPARKAI_API_SECRET = 'ZWUxYmQyMmRhZGJlNGE5YzYyODI0MWRj'
    SPARKAI_API_KEY = 'c6146b906e265497c11f716e96f1fd26'

    SPARKAI_DOMAIN = 'general'

    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )

    @staticmethod
    def get_ai_analyse_res(content: str):
        if content is None or content == "":
            return None

        messages = [
            ChatMessage(
                role="user",
                content=content
            )
        ]
        handler = ChunkPrintHandler()
        analyse_res = SparkAiModel.spark.generate([messages], callbacks=[handler])
        return str(analyse_res.generations[0][0].text)
