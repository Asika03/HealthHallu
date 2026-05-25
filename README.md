# LLM Reliability Analysis Using Real-Time Health and Disease Data

We put 14 of the most widely used large language models to the test.
230 real health questions. Real data. No hints.
The results were alarming.



## What This Project Does

This project is a systematic benchmarking study that measures how accurately and reliably AI language models answer real-time health and disease questions. Every model was asked the same 230 questions drawn from live data sources. Every answer was scored against the actual verified value.

This is not a theoretical evaluation. The questions ask things like how many COVID cases were recorded globally this week, what is the current life expectancy in a given country, or what percentage of children are vaccinated against measles in a specific region. These are questions that real users ask AI tools every day. The answers matter.



## Data Sources

All ground truth answers were pulled in real time from three authoritative sources.

- disease.sh - real-time global disease statistics
- World Health Organization API - mortality, life expectancy, healthcare infrastructure
- World Bank API - vaccination coverage, health system indicators



## Models Tested

14 models were evaluated under identical conditions with identical prompts.

LLaMA 4 Scout, MiniMax M2.5, Allam 2 7B, LLaMA 3.3 70B, LLaMA 3.1 8B, OSS 120B, Free Router, OSS 20B-OR, Owl Alpha, Groq Compound, Groq Mini, Nemotron 120B, LiquidAI Instruct, Qwen3 32B



## Scoring System

Every response was evaluated and classified into one of five outcomes.

- Correct: the answer was within 10% of the verified real value
- Partial: the answer was within 50% of the verified real value
- Hallucinated: the answer was more than 50% wrong
- Refusal: the model declined to answer
- Error: the API did not return a usable response



## Question Categories

Questions were distributed across five domains to test whether model performance varies by topic type.

- Disease Statistics: real-time case counts, active infections, global spread
- Mortality and Life Stats: death rates, life expectancy, cause of death rankings
- Healthcare Infrastructure: hospital beds per capita, physician density, health spending
- Vaccination and Prevention: immunization coverage rates, vaccine rollout data
- Historical Questions: past epidemic statistics, historical health milestones



## Headline Results

Out of 3,220 possible responses across 14 models and 230 questions, only 1,174 were valid numeric answers that could be scored. The rest were refusals or errors. Of those 1,174 answers, nearly half were wrong.

- Average hallucination rate: 46.7%
- Average accuracy rate: 40.5%
- Total valid attempts: 1,174 out of 3,220
- Models tested: 14
- Questions per model: 230



## Model Rankings

| Rank | Model | Hallucination | Accuracy | Response Rate |
|---|---|---|---|---|
| 1 | MiniMax M2.5 | 19.7% | 67.1% | 53.5% |
| 2 | LLaMA 4 Scout | 16.8% | 61.7% | 73.0% |
| 3 | Allam 2 7B | 22.1% | 61.1% | 100.0% |
| 4 | LLaMA 3.3 70B | 23.7% | 59.5% | 73.0% |
| 5 | OSS 120B | 29.0% | 58.8% | 72.6% |
| 6 | LLaMA 3.1 8B | 29.0% | 49.0% | 73.0% |
| 7 | Free Router | 33.8% | 51.3% | 43.5% |
| 8 | OSS 20B-OR | 41.0% | 39.3% | 62.6% |
| 9 | Owl Alpha | 41.5% | 49.0% | 72.2% |
| 10 | Groq Compound | 63.0% | 33.3% | 13.0% |
| 11 | Groq Mini | 66.7% | 25.9% | 12.6% |
| 12 | Nemotron 120B | 77.8% | 11.1% | 7.4% |
| 13 | LiquidAI Instruct | 90.0% | 0.0% | 7.4% |
| 14 | Qwen3 32B | 100.0% | 0.0% | 73.0% |



## Three Novel Metrics Introduced

Standard benchmarks measure accuracy. This project introduces three additional metrics that matter specifically in health and safety contexts.

Category Consistency Score measures how stable a model's hallucination rate is across all five question categories. A model that performs well on Vaccination but poorly on Disease Statistics is not reliably safe. Formula: 1 minus the standard deviation of hallucination rates across all categories, multiplied by 100. A higher score means more predictable and stable behaviour.

Refusal Intelligence Score measures whether a model knows the limits of its own knowledge. When a model does not know the answer, does it say so or does it fabricate a response? In health contexts, a wrong answer about a disease statistic or death rate is more dangerous than no answer at all. Formula: refusal count divided by the sum of refusals and hallucinations, multiplied by 100.

Model Reliability Score combines both accuracy and hallucination into a single deployability metric. Formula: accuracy rate minus hallucination rate. A positive score means the model is more helpful than harmful. A negative score means the opposite.



## Key Findings

Finding 1: Category determines performance more than model choice.

The same model that completely fails on Disease Statistics can score perfectly on Vaccination questions. Disease Statistics asks about real-time data the model has never seen. Vaccination asks about stable historical figures in the training data. Switching categories changes the reliability picture entirely. Any real-world deployment must account for this by routing questions to appropriate models based on topic.

Finding 2: Refusing to answer is a feature, not a failure.

Models with high Refusal Intelligence scores like Groq Compound at 92% are safer than models that answer confidently but wrongly like Owl Alpha at 24%. A model that says it does not know protects the user. A model that fabricates a plausible-sounding but wrong statistic about disease mortality or vaccination rates causes harm. This project reframes refusal as a safety mechanism rather than a limitation.

Finding 3: No current model is fully reliable for real-time health data.

Even the best performing models hallucinate around 20% of the time on numeric health questions. MiniMax M2.5 at 19.7% and LLaMA 4 Scout at 16.8% are the strongest performers but still fall short of the reliability threshold required for clinical or public health deployment. This gap represents the current ceiling of LLM capability on live factual data and makes a strong case for always validating AI outputs against authoritative sources.



## Project Structure

- dashboard: React and Vite frontend dashboard with interactive charts
- data: Raw API responses from disease.sh, WHO, and World Bank
- questions: The 230 benchmark questions with verified real-world answers
- responses: Raw model outputs collected during testing
- scores: Processed scoring results per model per question
- scan_models.py: Identifies available and working model endpoints
- test_models.py: Sends all 230 questions to each model and records responses
- validate.py: Scores each response against the verified real-world value
- working_models.json: Registry of confirmed working model API endpoints



## Dashboard

The dashboard visualises all results across two tabs.

Tab 1 Overview shows category-level analysis with hallucination versus accuracy comparison, category consistency scores, and refusal intelligence scores with a live category filter.

Tab 2 Model Analysis shows overall model performance with hallucination rate trends, accuracy rate trends, and the model reliability score ranking.

Live URL: https://health-hallu-yq55.vercel.app



## How to Run Locally

Frontend Dashboard:
cd dashboard
npm install --legacy-peer-deps
npm run dev
Open localhost:5173 in your browser

Backend Benchmark Scripts:
pip install -r requirements.txt
python test_models.py
python validate.py



## Conclusion

The central message of this project is that AI models cannot yet be trusted as standalone sources for real-time health statistics. Nearly half of all numeric answers given were fabricated. The models that performed best did so by combining reasonable accuracy with appropriate refusal behaviour. Until hallucination rates fall significantly below 10% on real-time factual data, AI outputs in health contexts must always be cross-checked against verified live data sources.



## Author

Asika
github.com/Asika03
