\# Project Description Document



\## 1. Project Overview



\### 1.1 Project Name



Canteen Voice Feedback Analysis System Based on Large Language Models



\### 1.2 Project Background



University canteens usually collect student feedback through paper suggestion boxes, instant messaging tools, or scattered online forms. These methods have problems such as low input efficiency, irregular feedback content, slow issue identification, and unclear shop-level archiving. This project builds a demonstrable and runnable graduation project system around “voice input + automatic analysis + shop-level display.”



\### 1.3 Project Objectives



\- Support users to record canteen feedback through a browser.

\- Automatically complete speech-to-text transcription, text cleaning, and structured semantic analysis.

\- Archive analysis results to the corresponding shop cards.

\- Display shop scores, issue categories, sentiment distribution, and trend charts.

\- Support export of shop analysis reports.



\## 2. System Functions



\### 2.1 Feedback Input



\- Support browser microphone recording.

\- When the user clicks Start Recording, the system first clears the previous recognized text and overview analysis results to avoid old data remaining.

\- After recording, the audio is uploaded and a transcription task is submitted.

\- After transcription is completed, the recognized text is displayed in the input box.

\- Users can manually correct the recognized text before submitting it for analysis.



\### 2.2 Text Processing and Intelligent Analysis



\- Remove oral fillers and repeated fragments.

\- Normalize basic text forms such as canteen floor expressions, spaces, and repeated content.

\- Use the large language model to match shops directly from the known shop list in the system, and output sentiment analysis, issue classification, key summary, urgency, and issue weights.

\- The current prompt has been improved to handle English aliases, similar pronunciations, split words, spelling errors, and synonymous expressions.

\- When the model is unavailable, quota is insufficient, or the output is abnormal, the system uses rule-based fallback analysis to return basic results. The fallback result prioritizes sentiment, issue category, and summary availability.



\### 2.3 Overview Analysis Area



\- Display the target shop.

\- Display sentiment tendency.

\- Display the main issue category.

\- Display urgency level.

\- Display the overall score.

\- Display system summary, sentiment scores, and issue weights.



\### 2.4 Shop Analysis Display Area



\- Display shop name, overall score, sentiment status, high-frequency issues, latest summary, total feedback count, today’s feedback count, and this week’s feedback count in shop cards.

\- Click a shop card to switch the linked charts on the right side.

\- Support shop report download.

\- Support viewing the current shop’s trend chart and issue category chart through a popup window.

\- Popup charts are reinitialized every time they are opened to ensure normal display after multiple openings.



\### 2.5 Charts and Report Area



\- Shop score comparison chart.

\- Issue category distribution chart.

\- Sentiment distribution chart.

\- Shop trend change chart.

\- Download the report of the currently selected shop.

\- The chart area on the right supports adaptive resizing with the page layout to reduce unnecessary blank space at the bottom of charts.



\## 3. Technical Architecture



\### 3.1 Frontend



\- Vue 3

\- Vite

\- Pinia

\- Vue Router

\- Element Plus

\- ECharts

\- Axios



\### 3.2 Backend



\- FastAPI

\- SQLAlchemy

\- SQLite

\- Pydantic Settings

\- Uvicorn

\- ReportLab



\### 3.3 Models and Services



\- Alibaba Cloud DashScope long-audio transcription API

\- Tongyi Qianwen API compatible with the OpenAI protocol

\- Large language model shop matching based on the known shop list

\- Local rule-based fallback analysis



\### 3.4 System Structure



The system uses a frontend-backend separation architecture:



\- The frontend is responsible for recording, page interaction, status display, chart rendering, and report download.

\- The backend is responsible for audio receiving, speech transcription task submission and polling, text cleaning, intelligent analysis, score calculation, database storage, and report generation.



\## 4. Directory Structure



```text

MealFeedbackAnalytics/

├─ backend/

│  ├─ app/

│  │  ├─ api/

│  │  ├─ core/

│  │  ├─ db/

│  │  ├─ models/

│  │  ├─ schemas/

│  │  ├─ services/

│  │  └─ utils/

│  ├─ data/

│  │  └─ seeds/

│  ├─ reports/

│  ├─ storage/

│  │  └─ audio/

│  ├─ main.py

│  ├─ pyproject.toml

│  └─ requirements.txt

├─ frontend/

│  ├─ src/

│  │  ├─ api/

│  │  ├─ components/

│  │  ├─ router/

│  │  ├─ stores/

│  │  ├─ styles/

│  │  └─ views/

│  ├─ index.html

│  ├─ package.json

│  └─ vite.config.ts

└─ docs/

&#x20;  ├─ Requirements Document.txt

&#x20;  ├─ Development Plan Document.md

&#x20;  ├─ Development Steps Document.md

&#x20;  └─ Project Description Document.md

```



\## 5. Core Business Workflow



1\. The user opens the frontend page and clicks Start Recording.

2\. The frontend clears the previous recognized text, analysis result, and related audio status.

3\. The browser requests microphone permission and records audio.

4\. After recording, the frontend uploads the audio to the backend.

5\. The backend submits an Alibaba Cloud long-audio transcription task, and the frontend polls the task status.

6\. After successful transcription, the recognized text is filled back into the frontend input box.

7\. The user clicks Submit Analysis.

8\. The backend performs text cleaning, large language model shop matching, multi-dimensional analysis, score calculation, and result storage.

9\. The frontend refreshes the overview analysis area, shop analysis display area, and charts and report area.

10\. The user can download a shop analysis report or view popup charts through the shop card.



\## 6. Data Storage Description



The system uses SQLite for local persistence and mainly includes the following data entities:



\- Shop table: stores shop name, category, aliases, current score, feedback count, and related information.

\- Feedback table: stores audio path, original text, cleaned text, language, and creation time.

\- Analysis result table: stores shop classification, sentiment scores, issue categories, issue weights, summary, urgency, and total score.

\- Shop statistics table: stores shop sentiment distribution, issue distribution, and trend point data.

\- Score history table: stores score change records of shops.



When the project is started for the first time, the database is automatically initialized and seed shops and sample feedback are imported.



\## 7. API Description



The unified backend prefix is `http://127.0.0.1:8000/api/v1`.



\### 7.1 System API



\- `GET /system`  

&#x20; Purpose: system health check.



\### 7.2 Speech Transcription APIs



\- `POST /asr/upload-and-submit`  

&#x20; Purpose: upload audio and submit a long-audio transcription task.



\- `GET /asr/tasks/{task\_id}`  

&#x20; Purpose: query transcription task status and recognized result.



\- `POST /asr/tasks/submit`  

&#x20; Purpose: manually submit a transcription task.



\### 7.3 Text Analysis API



\- `POST /feedback/analyze`  

&#x20; Purpose: submit a text analysis request and return shop, sentiment, issue category, weight, summary, and score results.



\### 7.4 Shop APIs



\- `GET /shops`  

&#x20; Purpose: get shop card list data.



\- `GET /shops/{shop\_id}`  

&#x20; Purpose: get detailed chart data of a single shop.



\### 7.5 Dashboard Summary API



\- `GET /dashboard/summary`  

&#x20; Purpose: get homepage charts and aggregated statistics.



\### 7.6 Report API



\- `GET /report/shops/{shop\_id}`  

&#x20; Purpose: download the PDF report of a specified shop.



\## 8. Runtime Environment



\### 8.1 Backend Environment



\- Python 3.12 or above

\- `uv` is recommended

\- Operating system: Windows / WSL / Linux



\### 8.2 Frontend Environment



\- Node.js 18 or above

\- npm



\## 9. Environment Variable Configuration



The backend reads configuration from `backend/.env`. At least the following variables are required:



```env

OSS\_BUCKET\_NAME=your OSS Bucket name

OSS\_ACCESS\_KEY\_ID=your OSS AccessKey ID

OSS\_ACCESS\_KEY\_SECRET=your OSS AccessKey Secret

DASHSCOPE\_API\_KEY=your DashScope API Key

```



\### 9.1 How to Apply for OSS Variables



The audio files of this project are first uploaded to Alibaba Cloud Object Storage Service OSS, and then read by Alibaba Cloud long-audio transcription service. Therefore, an OSS Bucket and related access credentials are required first.



\#### Step 1: Register and Log in to Alibaba Cloud



\- Open the Alibaba Cloud official website and complete account registration.

\- Log in and enter the console.



\#### Step 2: Enable OSS Service



\- Search for `Object Storage Service OSS` in the console.

\- If it is your first time entering the service, follow the page instructions to enable OSS.



\#### Step 3: Create a Bucket



\- Enter the OSS console and click Create Bucket.

\- The `Bucket name` must be globally unique. This value will be used as `OSS\_BUCKET\_NAME`.

\- The `Region` is recommended to be the same as or close to the speech transcription service region to reduce upload and reading delay.

\- Select standard storage as the storage type.

\- Set read/write permission to private. Do not make audio files publicly accessible.



After creation, you will get a Bucket name, for example:



```env

OSS\_BUCKET\_NAME=meal-feedback-audio-demo

```



\#### Step 4: Create an AccessKey



\- Enter AccessKey Management from the avatar menu in the upper-right corner of the Alibaba Cloud console.

\- Create a new AccessKey.

\- The system will provide:

&#x20; - `AccessKey ID`

&#x20; - `AccessKey Secret`



Fill these two values into:



```env

OSS\_ACCESS\_KEY\_ID=your AccessKey ID

OSS\_ACCESS\_KEY\_SECRET=your AccessKey Secret

```



Notes:



\- `AccessKey Secret` is fully displayed only once when it is created, so it must be saved immediately.

\- Do not submit these values to the Git repository or share screenshots with others.

\- It is recommended to create a separate access credential with minimum required permissions for this project.



\### 9.2 How to Apply for DASHSCOPE\_API\_KEY



This project uses two capabilities of Alibaba Cloud DashScope:



\- Long-audio speech transcription

\- Tongyi Qianwen large language model analysis



Therefore, `DASHSCOPE\_API\_KEY` is one of the most important configuration items of the system.



\#### Step 1: Enter DashScope / Alibaba Cloud Bailian Platform



\- Log in to Alibaba Cloud and enter the Bailian or DashScope console.

\- Confirm that the required model and API services have been enabled.



\#### Step 2: Create an API Key



\- Find API Key Management or Key Management in the console.

\- Create a new API Key.

\- Copy the key after creation. This value is:



```env

DASHSCOPE\_API\_KEY=your DashScope API Key

```



\#### Step 3: Confirm That Required Capabilities Are Enabled



At least two capabilities should be available:



\- Audio transcription capability

\- Tongyi Qianwen text model capability



If they are not enabled, the related API calls may return errors such as insufficient permission, insufficient quota, or service not authorized.



Additional notes:



\- If the DashScope console is set to free quota only mode and the free quota is used up, the model analysis API may return `403 Forbidden`.

\- In this case, speech transcription may still work, but text analysis will fall back to rule-based analysis.

\- To continuously use the large language model for shop matching and analysis, check the model service availability and quota settings in the console.



\### 9.3 How to Write the `.env` File



Create a `.env` file under the `backend/` directory and fill in your real values, for example:



```env

OSS\_BUCKET\_NAME=meal-feedback-audio-demo

OSS\_ACCESS\_KEY\_ID=your-real-AccessKeyID

OSS\_ACCESS\_KEY\_SECRET=your-real-AccessKeySecret

DASHSCOPE\_API\_KEY=your-real-DashScopeApiKey

```



Notes:



\- `DASHSCOPE\_API\_KEY` is used for both Alibaba Cloud long-audio transcription and Tongyi Qianwen analysis APIs.

\- The `.env.example` file in the repository should only be used as a field reference. During actual deployment, replace it with your own valid credentials.

\- The frontend default request address is `http://127.0.0.1:8000/api/v1`. It can be overwritten by `VITE\_API\_BASE\_URL` if needed.



\## 10. Startup Instructions



\### 10.1 Start the Backend



```bash

cd backend

uv run uvicorn main:app --reload

```



If `uv` is not used on the local machine, run:



```bash

cd backend

uvicorn main:app --reload

```



After startup, you can visit:



\- API documentation: `http://127.0.0.1:8000/docs`

\- Root path: `http://127.0.0.1:8000/`



\### 10.2 Start the Frontend



```bash

cd frontend

npm install

npm run dev

```



Default access address:



\- `http://127.0.0.1:5173`



Default interface language:



\- The system displays English by default after entering the page.

\- Users can switch between Chinese and English through the language switch button in the upper-right corner of the page.



\## 11. Demonstration Guide



The recommended demonstration order is:



\- Open the homepage and explain that the page consists of the feedback input area, overview analysis area, shop analysis display area, and charts and report area.

\- Click Start Recording and record a piece of canteen voice feedback.

\- Explain that the system automatically fills back the recognized text and supports manual correction.

\- Click Submit Analysis and show the overview analysis result.

\- Explain that the analysis result is automatically archived to the corresponding shop card.

\- Click a shop card to switch the chart focus on the right side.

\- Click the View Chart button in the shop card to show the trend chart and issue category distribution chart in the popup window.

\- Click Download Report to export the shop PDF report.



\## 12. Current Implementation Status



\### 12.1 Implemented Functions



\- Recording, audio upload, asynchronous transcription, and text filling.

\- Automatically clearing the previous recognized text and overview analysis result when starting a new recording.

\- Basic text cleaning and normalization of canteen floor expressions.

\- Shop matching, multi-dimensional analysis, and rule-based fallback based on the large language model.

\- Overview analysis display.

\- Shop card display and aggregated statistics update.

\- Four main chart displays.

\- Shop chart popup.

\- PDF report download.

\- Chinese-English bilingual interface and default English display.

