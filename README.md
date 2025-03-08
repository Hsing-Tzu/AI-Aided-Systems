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

---

### Detailed Steps:

1. **Data Reading**  
   - The `travel_reviews.csv` file is read, and the data is split into batches for subsequent processing.

2. **Data Cleaning and Preprocessing** → (Cleaned Data)  
   - Clean the CSV data to ensure proper formatting and perform basic preprocessing, such as handling missing values and ensuring correct data formats.

3. **Generate Travel Review Prompt Agent** → (Generated Prompt Content)  
   - Based on the cleaned data, a travel review writing prompt is generated for each batch (e.g., title, journey review, feedback, etc.).

4. **Data Processing Agent** → (Processed Data)  
   - The Data Processing Agent processes the data into a format suitable for writing and prepares it for the next steps.

5. **Web Search Agent** → (Fetched Relevant Information)  
   - The Web Search Agent uses the generated prompt to search for related information on locations, food, cultural backgrounds, etc., and provides valuable content for the “Further Reading” section of the article.

6. **Article Generation Agent** → (Generated Travel Review Article)  
   - The Article Generation Agent consolidates all the information and writes the complete travel review article, incorporating the “Further Reading” section.

7. **Result Integration and Publishing** → (Final Article Text)  
   - The results from all agents are integrated, the article is formatted for publishing, and it is saved as a final text file.

---

This workflow ensures that each step is clearly defined, with agents collaborating to complete their respective tasks and ultimately generate the final content ready for publication.
