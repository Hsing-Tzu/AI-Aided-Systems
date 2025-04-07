# AI-Aided-Systems

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

### Detailed Steps:

1. **Data Reading**  
   - **Option 1**: Upload a CSV file (e.g., `travel_reviews.csv`). The data is read and split into batches for subsequent processing.
   - **Option 2**: Directly input a short review, which skips the batch processing step.

2. **Data Cleaning and Preprocessing** → (Cleaned Data)  
   - For CSV data: Clean the data to ensure proper formatting and perform basic preprocessing, such as handling missing values and ensuring correct data formats.
   - For short review: Skip this step as the input is already structured.

3. **Generate Travel Review Prompt Agent** → (Generated Prompt Content)  
   - Based on the input data (CSV or short review), a travel review writing prompt is generated for each batch or review (e.g., title, journey review, feedback, etc.).

4. **Data Processing Agent** → (Processed Data)  
   - The Data Processing Agent processes the data into a format suitable for writing and prepares it for the next steps.

5. **Web Search Agent** → (Fetched Relevant Information)  
   - The Web Search Agent uses the generated prompt to search for related information on locations, food, cultural backgrounds, etc., and provides valuable content for the “Further Reading” section of the article.

6. **Article Generation Agent** → (Generated Travel Review Article)  
   - The Article Generation Agent consolidates all the information and writes the complete travel review article, incorporating the “Further Reading” section.

7. **Result Integration and Publishing** → (Final Article Text)  
   - The results from all agents are integrated, the article is formatted for publishing, and it is saved as a final text file.

8. **PostAgent** → (Published Article on Medium)  
   - The PostAgent uses the `post_to_medium` endpoint to publish the article to Medium. It saves the article to a file and executes the `postAI.py` script to handle the publishing process.

---

This workflow ensures that each step is clearly defined, with agents collaborating to complete their respective tasks and ultimately generate the final content ready for publication.