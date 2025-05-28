# AI-Aided-Systems


### [YouTube Introduction](https://youtu.be/b59AQjcYLHI)


## Agent Workflow

### Data Reading
      ↓  
### Data Cleaning and Preprocessing → (Cleaned Data)  
      ↓  
### Generate Travel Review Prompt Agent → (Generated Prompt Content)  
      ↓  
### Data Processing Agent → (Processed Data)  
      ↓  
### Web Search Agent → (Fetched Relevant Information)  
      ↓  
### Article Generation Agent → (Generated Travel Review Article)  
      ↓  
### Result Integration and Publishing → (Final Article Text)  
      ↓  
### PostAgent → (Published Article on Medium)

---

AI-Aided-Systems is a full-stack application designed to process travel reviews, generate detailed summaries, and interact with external APIs like Google Gemini. It includes a **FastAPI backend** and a **React frontend** to provide a seamless user experience for uploading files, generating reviews, refining content, and publishing articles to Medium.

---

## Features

### Backend
- **File Upload**: Upload CSV files containing travel reviews for processing.
- **AI-Powered Review Generation**: Generate detailed travel reviews using Google Gemini API.
- **WebSocket Communication**: Real-time interaction with the backend for generating responses and fetching additional information.
- **Evaluation and Refinement**: Evaluate and refine generated reviews based on user instructions.
- **Publish to Medium**: Publish generated articles directly to Medium.

### Frontend
- **Upload CSV Files**: Upload travel review data for processing.
- **Generate Reviews**: Generate detailed travel reviews from short inputs.
- **Refine Content**: Modify and refine generated reviews based on user instructions.
- **Evaluate Reviews**: Display evaluation scores for generated reviews.
- **Publish to Medium**: Publish generated articles directly to Medium.

---

## Installation

### Prerequisites
- Python 3.9 or later
- Node.js (v16 or later)
- npm or yarn
- Virtual environment (recommended)
- `.env` file with the following environment variables:
  ```
  GEMINI_API_KEY=<Your Google Gemini API Key>
  ```

---

### Backend Setup

1. **Navigate to the Backend Directory**
   ```bash
   cd AI-Aided-Systems
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv AAS-venv
   ```

3. **Activate Virtual Environment**
   - On Windows:
     ```bash
     .\AAS-venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source AAS-venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**
   Create a .env file in the root directory and add your `GEMINI_API_KEY`:
   ```
   GEMINI_API_KEY=<Your Google Gemini API Key>
   ```

6. **Run the Backend**
   ```bash
   uvicorn backend:app --reload
   ```

   The backend will be available at `http://127.0.0.1:8000`.

---

### Frontend Setup

1. **Navigate to the Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start the Frontend**
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`.

---

## Usage

### Backend Endpoints

1. **File Upload**
   - Endpoint: `POST /upload`
   - Description: Upload a CSV file containing travel reviews for processing.

2. **Generate Review**
   - Endpoint: `POST /generate_review`
   - Description: Generate a detailed travel review based on a short input.

3. **Refine Review**
   - Endpoint: `POST /refine_review`
   - Description: Refine an existing article based on user instructions.

4. **Evaluate Review**
   - Endpoint: `POST /evaluate_review`
   - Description: Evaluate the quality of a generated review.

5. **Publish to Medium**
   - Endpoint: `POST /post_to_medium`
   - Description: Publish a generated article to Medium.

6. **WebSocket Communication**
   - Endpoint: `ws://127.0.0.1:8000/ws`
   - Description: Real-time communication for generating responses and fetching additional information.

---

### Frontend Features

1. **Upload CSV Files**
   - Switch to the "Upload CSV" mode.
   - Select a CSV file and click "Upload CSV".
   - The backend will process the file and return a consolidated review.

2. **Generate Reviews**
   - Switch to the "Generate" mode.
   - Enter a short review in the input box and click "Generate Article".
   - The backend will generate a detailed review and display it in the list.

3. **Refine Content**
   - Enter a refinement instruction (e.g., "Make it more humorous") in the input box below a generated review.
   - Click "Regenerate" to apply the changes.

4. **Evaluate Reviews**
   - View evaluation scores for generated reviews, including completeness, emotional expression, and readability.

5. **Publish to Medium**
   - Click "Publish to Medium" to post the latest generated review to Medium.

---

## Development

### Backend Development

1. **Install Development Dependencies**
   ```bash
   pip install -r dev-requirements.txt
   ```

2. **Run the Backend**
   ```bash
   uvicorn backend:app --reload
   ```

3. **Run Tests**
   ```bash
   pytest
   ```

---

### Frontend Development

1. **Start the Frontend**
   ```bash
   npm start
   ```

2. **Connect to the Backend**
   Ensure the backend is running at `http://localhost:8000`.

---

## Deployment

### Backend Deployment

1. **Build and Activate Virtual Environment**
   ```bash
   python -m venv AAS-venv
   .\AAS-venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Backend**
   ```bash
   uvicorn backend:app --host 0.0.0.0 --port 8000
   ```

---

### Frontend Deployment

1. **Build the Application**
   ```bash
   npm run build
   ```

2. **Serve the Build**
   Deploy the contents of the `build` folder to a static hosting service (e.g., Netlify, Vercel, or an Nginx server).

---

## Troubleshooting

- **Backend Connection Issues**: Ensure the backend is running at `http://localhost:8000`.
- **CORS Errors**: Update the backend's CORS settings to allow requests from the frontend's domain.
- **Missing Dependencies**: Run `npm install` or `pip install -r requirements.txt` to ensure all dependencies are installed.
