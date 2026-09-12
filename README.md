---
title: CodeLATS
emoji: 🏃
colorFrom: gray
colorTo: yellow
sdk: streamlit
sdk_version: 1.27.1
app_file: app.py
pinned: true
license: mit
---

# CodeLATS

CodeLATS is a Streamlit app that generates a Python function from a natural-language coding problem. It asks an OpenAI chat model for Python code, generates Python `assert` tests, executes a sampled test, and uses failed-test feedback and model self-reflection to generate more candidates.

The search code follows the Language Agent Tree Search (LATS) approach described in the [project paper](https://arxiv.org/abs/2310.04406). The current factory path supports Python only.

## Benchmark status

This checkout is a demo, not a complete benchmark runner. It contains no HumanEval or LeetCode dataset, benchmark command, pass@k aggregation script, or saved benchmark results. `PyExecutor.evaluate` has a HumanEval-specific helper, but the Streamlit app does not call it. The app also parses an `--is_leetcode` argument while building its internal arguments, but the current execution path does not use that flag.

This README makes no SOTA or pass@1 claim. Reproduce a result with a fixed model, prompt, test set, and parameter set before reporting it.

## Setup

Use Python 3.11 or later. The code calls `sys.set_int_max_str_digits`, which is not available on older Python versions.

```bash
git clone https://github.com/artur-shlyapnikov/lats-implementation.git
cd lats-implementation
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The root `requirements.txt` contains the dependencies for the Streamlit app, including `streamlit`, `openai==0.27.0`, `jsonlines`, `datasets`, `tenacity`, `astunparse`, and `accelerate`.

## Run the app

Run the command from the repository root because `app.py` adds `./lats` to Python's import path.

```bash
streamlit run app.py
```

Enter an OpenAI API key in the sidebar, describe the coding problem in the text area, set the search parameters if needed, and click **Send**. The app displays the generated Python function in the page. It does not write the result or search trace to a file.

The controls map to the code as follows.

| Control | Range and default | Effect |
| --- | --- | --- |
| Coding problem | Non-empty text | Becomes the function prompt. The app appends `Name the function answer()`. |
| OpenAI API key | Required | Assigned to `openai.api_key` when **Send** is clicked. |
| Tree Width | 1 to 5, default 1 | Passed as `n_samples`, the number of candidates generated during each expansion. |
| Tree Depth | 1 to 8, default 3 | Passed as `depth`, but the current search loop ignores it. Node depth starts at 0 and increments for each child. |
| Iterations | 1 to 4, default 2 | Passed as `max_iters`, the number of improvement-loop iterations after the initial candidate. |

## Search flow

For each request, the current implementation does the following.

1. It asks the model to generate Python `assert` statements for the prompt and keeps syntactically valid assertions.
2. It samples one generated test and asks the model for an initial implementation of `answer()`.
3. `PyExecutor` runs the implementation against that test. Each test gets a five-second thread timeout.
4. If the test fails, the model writes a self-reflection based on the implementation and the test feedback.
5. For each improvement iteration, the search selects a node with the highest UCT score, expands it with `n_samples` new implementations, and runs the child implementations against one randomly sampled test.
6. The reward is the fraction of sampled tests that pass. With the current one-test sample, the reward is either 0 or 1. The code adds that reward to the child and each of its ancestors.
7. If the initial candidate did not pass, the final fallback selects the immediate child of the root with the highest accumulated value and returns its function text.

The node records a candidate implementation, its parent and children, visit count, accumulated value, test feedback, reflection, and depth. The MCTS branch uses the accumulated-context reflexion prompt when it asks for a new implementation. The context collector includes feedback and reflections from at most two nodes on the selected path.

## API key and execution safety

The Streamlit app requires a key in its password field. It assigns the value to the OpenAI client configuration only after both the key and coding problem are present. `lats/utils.py` also initializes the OpenAI key from the `OPENAI_API_KEY` environment variable when that module is imported. Do not put a key in the repository or commit it to Git.

The executor runs model-generated function code and model-generated tests with Python `exec` in the application process. This is not a sandbox. Use an isolated environment and submit only code you trust.

## Current limits

- The generator and executor factories accept `py` and `python`; other languages are rejected even though the repository contains a Cargo harness skeleton.
- The app uses the legacy OpenAI Python 0.27.0 `ChatCompletion` interface. The default model selector is `gpt-4-turbo-preview`.
- The search code does not set its `is_solved` flag. After an initial failure, it therefore uses the final root-child value selection described above.
- The model-generated tests are the only tests used by the app. The repository does not provide a separate trusted test suite for arbitrary prompts.
- If test generation returns no syntactically valid assertions, the executor receives an empty test list and the current code has no fallback test source.

## Citation

If you use this implementation, cite the LATS paper:

```bibtex
@misc{zhou2023language,
      title={Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models},
      author={Andy Zhou and Kai Yan and Michal Shlapentokh-Rothman and Haohan Wang and Yu-Xiong Wang},
      year={2023},
      eprint={2310.04406},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```
