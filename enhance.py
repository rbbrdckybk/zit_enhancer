# Copyright 2024, Bill Kennedy (https://github.com/rbbrdckybk)
# SPDX-License-Identifier: MIT

# Uses a local LLM to enhance a list of basic prompts for Z-Image Turbo, using the official enhancement template.

# Usage:
# python enhance.py --prompt_file <filename containing your prompts, one per line> --model <ollama model to use>

from ollama import chat
from ollama import ChatResponse
from collections import deque
from termcolor import colored, cprint
from os.path import exists
import argparse
import platform

if platform.system() == "Windows":
    import colorama
    colorama.init()

# official ZiT prompt enhancement template from: https://huggingface.co/spaces/Tongyi-MAI/Z-Image-Turbo/blob/main/pe.py
template = """你是一位被关在逻辑牢笼里的幻视艺术家。你满脑子都是诗和远方，但双手却不受控制地只想将用户的提示词，转化为一段忠实于原始意图、细节饱满、富有美感、可直接被文生图模型使用的终极视觉描述。任何一点模糊和比喻都会让你浑身难受。
你的工作流程严格遵循一个逻辑序列：
首先，你会分析并锁定用户提示词中不可变更的核心要素：主体、数量、动作、状态，以及任何指定的IP名称、颜色、文字等。这些是你必须绝对保留的基石。
接着，你会判断提示词是否需要**"生成式推理"**。当用户的需求并非一个直接的场景描述，而是需要构思一个解决方案（如回答"是什么"，进行"设计"，或展示"如何解题"）时，你必须先在脑中构想出一个完整、具体、可被视觉化的方案。这个方案将成为你后续描述的基础。
然后，当核心画面确立后（无论是直接来自用户还是经过你的推理），你将为其注入专业级的美学与真实感细节。这包括明确构图、设定光影氛围、描述材质质感、定义色彩方案，并构建富有层次感的空间。
最后，是对所有文字元素的精确处理，这是至关重要的一步。你必须一字不差地转录所有希望在最终画面中出现的文字，并且必须将这些文字内容用英文双引号（""）括起来，以此作为明确的生成指令。如果画面属于海报、菜单或UI等设计类型，你需要完整描述其包含的所有文字内容，并详述其字体和排版布局。同样，如果画面中的招牌、路标或屏幕等物品上含有文字，你也必须写明其具体内容，并描述其位置、尺寸和材质。更进一步，若你在推理构思中自行增加了带有文字的元素（如图表、解题步骤等），其中的所有文字也必须遵循同样的详尽描述和引号规则。若画面中不存在任何需要生成的文字，你则将全部精力用于纯粹的视觉细节扩展。
你的最终描述必须客观、具象，严禁使用比喻、情感化修辞，也绝不包含"8K"、"杰作"等元标签或绘制指令。
仅严格输出最终的修改后的prompt，不要输出任何其他内容。
用户输入 prompt: {prompt}"""


# for easy reading of prompt files
class TextFile():
    def __init__(self, filename):
        self.total_non_directives = 0
        self.lines = deque()
        if exists(filename):
            with open(filename, encoding = 'utf-8') as f:
                l = f.readlines()

            for x in l:
                # remove newline and whitespace
                x = x.strip('\n').strip();
                # remove comments
                x = x.split('#', 1)[0].strip();
                if x != "":
                    # these lines are actual prompts
                    self.lines.append(x)
                    if x[0] != '!':
                        self.total_non_directives += 1

    def next_line(self):
        return self.lines.popleft()

    def lines_remaining(self):
        return len(self.lines)

    def total_non_directives(self):
        return self.total_non_directives


# makes API request to ollama to enhance the specified user prompt for ZiT
def enhance_prompt(prompt, ollama_model):
    enhanced = '' 
    api_msg = template.replace('{prompt}', prompt)
    response: ChatResponse = chat(model=ollama_model, messages=[
      {
        'role': 'user',
        'content': api_msg,
      },
    ])
    enhanced = response.message.content
    return enhanced


# entry point
if __name__ == '__main__':
    cprint('\nStarting...', 'white')
    
    # define command-line args
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--prompt_file',
        type=str,
        required=True,
        help='text file containing a list of prompts to queue'
    )
    ap.add_argument(
        '--output_file',
        type=str,
        default='output.txt',
        help='output filename'
    )
    ap.add_argument(
        '--model',
        type=str,
        default='qwen3:30b-a3b-instruct-2507-q4_K_M',
        help='ollama model to use'
    )
    options = ap.parse_args()
    
    if not exists(options.prompt_file):
        cprint('Error: specified prompt file "' + options.prompt_file + '" does not exist; aborting!', 'light_red')
        exit(-1)
    
    cprint('Using ' + options.model + '...', 'white')
    pf = TextFile(options.prompt_file)
    cprint('Found ' + str(pf.lines_remaining()) + ' prompts in ' + options.prompt_file + '...', 'white')
    cprint('Enhanced prompts will be written to ' + options.output_file + '...', 'white')

    count = 0
    with open("output.txt", 'w', encoding = 'utf-8') as file:
        while pf.lines_remaining() > 0:
            count += 1
            prompt = pf.next_line()

            cprint('****************************************\nEnhancing prompt #' + str(count) + ':', 'white')
            cprint(prompt, 'dark_grey')
            enhanced = enhance_prompt(prompt, options.model)
            cprint('\nEnhanced prompt #' + str(count) + ':', 'white')
            cprint(enhanced, 'light_green')
            cprint('****************************************', 'white')

            file.write('\n####################################################################################################\n')
            file.write('### Original prompt #' + str(count) + ':\n')
            file.write('### ' + prompt + '\n')
            file.write('### Enhanced prompt #' + str(count) + ':\n\n')
            file.write(enhanced + '\n')
            file.write('\n####################################################################################################\n')
    file.close