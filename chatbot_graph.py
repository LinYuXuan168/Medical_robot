from question_classifier import *
from question_parser import *
from answer_search import *
from zhipuai import ZhipuAI


# 问答类
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是小黑医药智能助理，希望可以帮到您。如果没答上来，可联系人工助理。祝您身体棒棒！'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        # print(res_sql)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)


if __name__ == '__main__':
    handler = ChatBotGraph()
    client = ZhipuAI(api_key="34ce6c9885554de79b71b390b62c7a42.PU5uiMj1kuRfxTUn")  # 请填写您自己的APIKey
    while 1:
        question = input('用户：')
        answer = handler.chat_main(question)
        print(f'润色前的答案{answer}')
        response = client.chat.completions.create(
            model="glm-4-plus",  # 请填写您要调用的模型名称
            messages=[
                {"role": "user", "content": "以一名医生的口吻润色{}这句话,给我最终版本就可以".format(answer)},
            ],
        )
        final_answer = response.choices[0].message.content
        print('小黑:', final_answer)

