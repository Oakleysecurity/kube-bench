from openai import OpenAI
from ruamel.yaml import YAML
import os

client = OpenAI(
    api_key="OPENAI_API_KEY",
    base_url="https://exmple.com"
)

# 初始化 YAML 解析器
yaml = YAML()
yaml.preserve_quotes = True  # 保留原始文件的引号
yaml.indent(mapping=2, sequence=4, offset=2)  # 设置缩进格式

def askChatGPT(text):
    messages = [{"role": "system", "content": "你是一个资深的云原生安全专家，同时精通英语和汉语，能够准确的翻译各种英文技术文章和句子。1、我每一次会给你发一个云原生安全领域的英文句子或段落，你需要将它翻译成中文。2、翻译的结果应该尽量准确，并且不要太死板生硬。3、翻译时应该保留专有名词、系统组件名称、参数名称等。4、你在回复对话的时候只需要回复翻译的结果。"},
        {"role": "user", "content": "If using a Kubelet config file, edit the file to set authentication: anonymous: enabled to false."},
        {"role": "assistant", "content": "如果使用 Kubelet 配置文件，编辑该文件，将 authentication: anonymous: enabled 设置为 false。"},
        ]
    d = {"role":"user","content":text}
    messages.append(d)
    MODEL = "gpt-3.5-turbo"
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages = messages,
            temperature=1)
        translation = response.choices[0].message.content.strip()
        return "".join(translation.splitlines()) # 去除多余换行
    except Exception as e:
        print(f"翻译失败: {e}")
        return text

def process_yaml(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
    def translate_fields(item):
        if isinstance(item, dict):
            for key, value in item.items():
                if key in ['text', 'remediation'] and isinstance(value, str):
                    print(f"正在翻译字段: {key}")
                    item[key] = askChatGPT(value)
                else:
                    translate_fields(value)
        elif isinstance(item, list):
            for sub_item in item:
                translate_fields(sub_item)
    translate_fields(data)
    
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_file):
        open(output_file, 'w').close()
        
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


def main():
    base_dir = "/path/to/source/cfg/"  # 输入目录
    output_base_dir = "/path/to/target/cfg/" # 输出目录
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.yaml'):
                input_file = os.path.join(root, file)
                # 在输出目录中保持相对路径结构
                relative_path = os.path.relpath(input_file, base_dir)
                output_file = os.path.join(output_base_dir, relative_path)
                print(f"正在处理文件: {input_file}")
                try:
                    process_yaml(input_file, output_file)
                    print(f"文件已处理并保存到: {output_file}")
                except Exception as e:
                    print(f"处理文件 {input_file} 时出错: {e}")
main()