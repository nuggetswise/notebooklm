# Centralized Prompt Management System

## Overview

The Email RAG system now uses a centralized prompt management system that makes all prompts easily maintainable, versionable, and customizable. This eliminates the need to hunt through code files to find and modify prompts.

## 🎯 **Key Benefits**

### ✅ **Centralized Management**
- All prompts in one place (`rag/prompts.py`)
- Easy to find, edit, and version prompts
- Consistent prompt structure across the system

### ✅ **Type Safety**
- Enum-based prompt types prevent typos
- Variable validation ensures all required parameters are provided
- Clear error messages for missing variables

### ✅ **Version Control**
- Each prompt has a version field
- Easy to track changes and rollback if needed
- Clear documentation of prompt evolution

### ✅ **Testing & Validation**
- Built-in prompt testing via API endpoints
- Frontend interface for testing prompts with sample data
- Immediate validation of prompt changes

## 📋 **Available Prompt Types**

### 1. **RAG Query Prompts**
- `rag_query` - Basic RAG queries without persona context
- `rag_query_with_persona` - Enhanced RAG queries with sender persona information

### 2. **Persona Management**
- `persona_context` - Generate contextual information about email senders
- `topic_extraction` - Extract topics from email content using AI
- `sentiment_analysis` - Analyze sentiment of email content

### 3. **Email Processing**
- `email_summary` - Generate concise summaries of email content
- `fallback_response` - Fallback responses when AI services are unavailable

## 🛠 **Usage Examples**

### Basic Usage
```python
from rag.prompts import prompt_manager, PromptType

# Get a formatted prompt
prompt = prompt_manager.get_prompt(
    PromptType.RAG_QUERY,
    question="What is this email about?",
    context_text="Email content here..."
)
```

### Advanced Usage with Persona Context
```python
# Get RAG query with persona context
prompt = prompt_manager.get_rag_query_prompt(
    question="What did Nate say about AI?",
    context_docs=retrieved_documents,
    persona_context="This email is from Nate. They typically write about AI and Tech."
)
```

### Persona Context Generation
```python
persona = {
    'first_name': 'Nate',
    'sender': 'nate@example.com',
    'email_count': 5,
    'topics': ['AI', 'Tech'],
    'labels': ['Newsletter']
}

context = prompt_manager.get_persona_context_prompt(persona)
```

## 🔧 **API Endpoints**

### Get All Prompts
```bash
GET /prompts
```
Returns all available prompts with metadata.

### Get Specific Prompt
```bash
GET /prompts/{prompt_type}
```
Returns a specific prompt template.

### Update Prompt
```bash
POST /prompts/{prompt_type}
{
    "template": "New prompt template...",
    "description": "Updated description",
    "version": "1.1"
}
```

### Test Prompt
```bash
GET /prompts/test/{prompt_type}?variable1=value1&variable2=value2
```
Test a prompt with provided variables.

## 🎨 **Frontend Management**

### Prompt Manager Interface
Run the prompt manager frontend:
```bash
streamlit run frontend/prompt_manager.py
```

**Features:**
- 📋 **View All Prompts** - Browse all available prompts with metadata
- ✏️ **Edit Prompts** - Modify prompt templates, descriptions, and versions
- 🧪 **Test Prompts** - Test prompts with sample data and see formatted output

### Usage Workflow
1. **View** prompts to understand current templates
2. **Edit** prompts to improve or customize them
3. **Test** prompts to ensure they work correctly
4. **Apply** changes immediately (no restart required)

## 📝 **Prompt Template Structure**

Each prompt template includes:
```python
PromptTemplate(
    name="Human-readable name",
    template="Template with {variables}",
    description="What this prompt does",
    variables=["list", "of", "required", "variables"],
    version="1.0"
)
```

## 🔄 **Integration Points**

### RAG Generator
The generator now uses centralized prompts:
```python
# Old way (hardcoded)
prompt = f"Based on the following content: {context}\nQuestion: {query}"

# New way (centralized)
prompt = prompt_manager.get_rag_query_prompt(query, context_docs)
```

### Persona Extractor
Topic extraction uses centralized prompts:
```python
# Old way (keyword-based)
topics = extract_keywords(text)

# New way (AI-powered with centralized prompts)
topics = generator.extract_topics(subject, content)
```

## 🚀 **Adding New Prompts**

### 1. Define New Prompt Type
```python
class PromptType(Enum):
    NEW_PROMPT = "new_prompt"
```

### 2. Add Template
```python
def _initialize_prompts(self):
    return {
        # ... existing prompts ...
        PromptType.NEW_PROMPT.value: PromptTemplate(
            name="New Prompt",
            template="Your template with {variables}",
            description="What this prompt does",
            variables=["variables"],
            version="1.0"
        )
    }
```

### 3. Add Helper Method
```python
def get_new_prompt(self, **kwargs) -> str:
    return self.get_prompt(PromptType.NEW_PROMPT, **kwargs)
```

## 🔍 **Troubleshooting**

### Common Issues

**1. Missing Variables Error**
```
ValueError: Missing required variables for rag_query: ['question']
```
**Solution:** Ensure all required variables are provided.

**2. Unknown Prompt Type**
```
ValueError: Unknown prompt type: invalid_prompt
```
**Solution:** Use valid PromptType enum values.

**3. Template Format Error**
```
KeyError: 'variable_name'
```
**Solution:** Check template syntax and variable names.

### Debug Tips

1. **Test Prompts** using the frontend interface
2. **Check Variables** in the prompt template
3. **Validate Format** of template strings
4. **Use API Endpoints** to test prompts programmatically

## 📊 **Monitoring & Analytics**

### Prompt Usage Tracking
The system can be extended to track:
- Which prompts are used most frequently
- Prompt performance metrics
- User feedback on prompt quality
- A/B testing of different prompt versions

### Version Management
- Track prompt changes over time
- Rollback to previous versions if needed
- Compare prompt effectiveness across versions

## 🎯 **Best Practices**

### 1. **Keep Prompts Clear**
- Use simple, direct language
- Avoid overly complex instructions
- Test with various inputs

### 2. **Version Control**
- Increment version numbers when making changes
- Document what changed and why
- Test thoroughly before deploying

### 3. **Variable Naming**
- Use descriptive variable names
- Document what each variable should contain
- Validate variable content when possible

### 4. **Testing**
- Test prompts with edge cases
- Validate output quality
- Monitor for unexpected behavior

## 🔮 **Future Enhancements**

### Planned Features
- **Prompt Templates** - Reusable prompt components
- **Conditional Logic** - Dynamic prompt selection
- **Multi-language Support** - Internationalized prompts
- **Performance Metrics** - Track prompt effectiveness
- **A/B Testing** - Compare prompt variations

### Integration Opportunities
- **Prompt Marketplace** - Share and import prompts
- **AI-powered Optimization** - Automatically improve prompts
- **Collaborative Editing** - Team-based prompt management
- **Version Control Integration** - Git-based prompt history

---

This centralized prompt system makes your email RAG system much more maintainable and allows for easy experimentation with different prompt strategies. The frontend interface makes it accessible to non-technical users while the API provides programmatic access for developers. 