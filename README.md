# Z-Image Turbo Prompt Enhancer
Prompt Enhancer for [Z-Image Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo), using a local Ollama instance.

Simple command-line utility that will utilize a local Ollama instance to enhance prompts for Z-Image Turbo, using [the official suggested enhancement template](https://huggingface.co/spaces/Tongyi-MAI/Z-Image-Turbo/blob/main/pe.py). Prompts must be supplied in a text file (one prompt per line).

I get good results on a 12GB 3060 with a [Q4_K_M quantized Qwen 3 2507](https://ollama.com/library/qwen3:30b-a3b-instruct-2507-q4_K_M) model.

# Usage
```
python enhance.py --prompt_file <filename containing your prompts, one per line> --model <ollama model to use>
```

For additional options, run ```python enhance.py --help```.
