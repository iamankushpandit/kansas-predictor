from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import joblib
import os
from groq import Groq
from ml_models import ClaimsPredictionModel
import json
from dotenv import load_dotenv
import matplotlib.pyplot as plt
# import seaborn as sns
import io
import base64
from matplotlib.dates import DateFormatter
import numpy as np

load_dotenv()

app = FastAPI(title="Kansas Claims Predictor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
predictor = None
groq_client = None
groq_usage_count = 0
MAX_DAILY_GROQ_REQUESTS = 100

# Pydantic models
class PredictionRequest(BaseModel):
    county: str
    claim_type: str
    target_date: str

class ChatRequest(BaseModel):
    message: str

class PredictionResponse(BaseModel):
    county: str
    claim_type: str
    date: str
    predicted_count: int
    predicted_cost: float
    avg_cost_per_claim: float

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global predictor, groq_client
    
    # Initialize Groq client
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", "your-groq-api-key-here"))
    
    # Load ML models
    predictor = ClaimsPredictionModel()
    
    # Load data and models if they exist
    if os.path.exists('../data/kansas_claims_10years.csv'):
        predictor.load_data('../data/kansas_claims_10years.csv')
        
    if os.path.exists('../models/claims_models.pkl'):
        predictor.load_models('../models/claims_models.pkl')
    else:
        # Train models if not saved
        print("Training models...")
        predictor.train_all_models()
        predictor.save_models('../models/claims_models.pkl')

@app.get("/")
async def root():
    return {"message": "Kansas Claims Predictor API"}

@app.get("/counties")
async def get_counties():
    """Get list of Kansas counties"""
    if predictor and predictor.data is not None:
        counties = sorted(predictor.data['county'].unique().tolist())
        return {"counties": counties}
    return {"counties": []}

@app.get("/claim-types")
async def get_claim_types():
    """Get list of claim types"""
    if predictor and predictor.data is not None:
        claim_types = sorted(predictor.data['claim_type'].unique().tolist())
        return {"claim_types": claim_types}
    return {"claim_types": []}

@app.post("/predict", response_model=PredictionResponse)
async def predict_claims(request: PredictionRequest):
    """Predict claims for specific county, type, and date"""
    if not predictor:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    try:
        prediction = predictor.predict_claims(
            request.county, 
            request.claim_type, 
            request.target_date
        )
        
        if not prediction:
            raise HTTPException(status_code=404, detail="No model found for this county/claim type")
        
        return PredictionResponse(**prediction)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict-range/{county}/{claim_type}")
async def predict_date_range(county: str, claim_type: str, days: int = 30):
    """Predict claims for multiple future dates"""
    if not predictor:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    try:
        start_date = datetime.now().strftime('%Y-%m-%d')
        predictions = predictor.predict_multiple_dates(county, claim_type, start_date, days)
        return {"predictions": predictions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary/{county}")
async def get_county_summary(county: str):
    """Get summary statistics for a county"""
    if not predictor:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    try:
        summary = predictor.get_county_summary(county)
        return {"county": county, "summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insights/{county}/{claim_type}")
async def get_seasonal_insights(county: str, claim_type: str):
    """Get seasonal patterns for county and claim type"""
    if not predictor:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    try:
        insights = predictor.get_seasonal_insights(county, claim_type)
        if not insights:
            raise HTTPException(status_code=404, detail="Insufficient data for insights")
        
        return {"county": county, "claim_type": claim_type, "insights": insights}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_llm(request: ChatRequest):
    """Chat interface for claims predictions"""
    global groq_usage_count
    
    if not predictor:
        raise HTTPException(status_code=500, detail="Predictor not available")
    
    try:
        # Process the user's message and get relevant data
        context = await process_user_query(request.message)
        
        # Generate response
        if groq_client and groq_usage_count < MAX_DAILY_GROQ_REQUESTS:
            groq_usage_count += 1
            response = await generate_formatted_response(request.message, context)
        else:
            response = generate_fallback_response(request.message, context)
        
        return {
            "response": response,
            "context": context,
            "usage": {
                "groq_requests_used": groq_usage_count,
                "groq_requests_limit": MAX_DAILY_GROQ_REQUESTS,
                "limit_reached": groq_usage_count >= MAX_DAILY_GROQ_REQUESTS
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_user_query(message: str):
    """Extract information from user query and get relevant predictions"""
    message_lower = message.lower()
    context = {}
    
    print(f"Processing query: {message_lower}")
    
    # Simple keyword extraction (can be enhanced)
    counties = predictor.data['county'].unique() if predictor.data is not None else []
    claim_types = ['emergency', 'inpatient', 'outpatient', 'pharmacy', 'mental_health', 'preventive']
    
    # Find mentioned county
    mentioned_county = None
    for county in counties:
        if county.lower() in message_lower:
            mentioned_county = county
            break
    
    # Find mentioned claim type - enhanced detection
    mentioned_claim_type = None
    if 'mental health' in message_lower or 'mental' in message_lower:
        mentioned_claim_type = 'mental_health'
    elif 'emergency' in message_lower:
        mentioned_claim_type = 'emergency'
    elif 'inpatient' in message_lower:
        mentioned_claim_type = 'inpatient'
    elif 'outpatient' in message_lower:
        mentioned_claim_type = 'outpatient'
    elif 'pharmacy' in message_lower or 'drug' in message_lower:
        mentioned_claim_type = 'pharmacy'
    elif 'preventive' in message_lower or 'prevention' in message_lower:
        mentioned_claim_type = 'preventive'
    
    print(f"Detected county: {mentioned_county}, claim type: {mentioned_claim_type}")
    
    # For seasonal trends, try to get insights even without specific county
    if 'seasonal' in message_lower or 'trend' in message_lower:
        if mentioned_claim_type:
            try:
                # Try with a default county if none specified
                test_county = mentioned_county or 'Johnson'
                print(f"Getting seasonal insights for {test_county}, {mentioned_claim_type}")
                insights = predictor.get_seasonal_insights(test_county, mentioned_claim_type)
                context['insights'] = insights
                context['detected_county'] = test_county
                print(f"Got insights: {insights}")
            except Exception as e:
                print(f"Error getting insights: {str(e)}")
                context['error'] = str(e)
        # Return early to avoid overwriting context
        context['detected_claim_type'] = mentioned_claim_type
        return context
    
    # Get predictions and insights for other cases
    try:
        # If specific county and claim type mentioned
        if mentioned_county and mentioned_claim_type:
            # Get next week's predictions
            start_date = datetime.now().strftime('%Y-%m-%d')
            predictions = predictor.predict_multiple_dates(
                mentioned_county, mentioned_claim_type, start_date, 7
            )
            context['predictions'] = predictions
            
            # Get seasonal insights
            insights = predictor.get_seasonal_insights(mentioned_county, mentioned_claim_type)
            context['insights'] = insights
            
    except Exception as e:
        context['error'] = str(e)
        print(f"Error getting insights: {str(e)}")
    
    if not context.get('detected_county'):
        context['detected_county'] = mentioned_county
    context['detected_claim_type'] = mentioned_claim_type
    
    return context

def generate_chart(data, chart_type, title, county=None, claim_type=None):
    """Generate chart and return as base64 string"""
    try:
        print(f"Generating chart: {chart_type} with data: {data}")
        
        plt.style.use('default')
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['axes.edgecolor'] = 'gray'
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['grid.alpha'] = 0.3
        fig, ax = plt.subplots(figsize=(6, 3.5))
        
        if chart_type == 'seasonal_trends':
            # Monthly trends chart
            months = list(data.keys())
            values = list(data.values())
            
            line = ax.plot(months, values, marker='o', linewidth=3, markersize=8, 
                          color='#1976d2', label=f'{claim_type.replace("_", " ").title()} Claims')
            ax.set_title(f'{title}', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Claims Count', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right', fontsize=11)
            
            # Add value labels on points
            for i, v in enumerate(values):
                ax.annotate(f'{v:,.0f}', (months[i], v), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=9)
            
        elif chart_type == 'cost_comparison':
            # Bar chart for cost comparison
            categories = list(data.keys())
            values = list(data.values())
            colors = ['#1976d2', '#42a5f5', '#90caf9', '#64b5f6', '#2196f3']
            
            bars = ax.bar(categories, values, color=colors[:len(categories)])
            ax.set_title(f'{title}', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Cost ($)', fontsize=12)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}', ha='center', va='bottom', fontsize=10)
            
            # Add legend
            ax.legend(bars, categories, loc='upper right', fontsize=11)
        
        elif chart_type == 'prediction_timeline':
            # Timeline prediction chart
            dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in data]
            counts = [item['predicted_count'] for item in data]
            
            line = ax.plot(dates, counts, marker='o', linewidth=3, markersize=8, 
                          color='#1976d2', label='Predicted Claims')
            ax.set_title(f'{title}', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Predicted Claims', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right', fontsize=11)
            
            # Add value labels on points
            for i, (date, count) in enumerate(zip(dates, counts)):
                if i % 2 == 0:  # Show every other label to avoid crowding
                    ax.annotate(f'{count:,.0f}', (date, count), textcoords="offset points", 
                               xytext=(0,10), ha='center', fontsize=9)
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(DateFormatter('%m/%d'))
            plt.xticks(rotation=45)
        
        # Add source attribution
        fig.text(0.99, 0.01, 'Kansas Claims Predictor', ha='right', va='bottom', 
                 fontsize=8, alpha=0.7, style='italic')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        print(f"Chart generated successfully, base64 length: {len(image_base64)}")
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        plt.close()
        return None

async def generate_formatted_response(message: str, context: dict):
    """Generate formatted response using Groq with charts"""
    
    # Generate chart if applicable
    chart_data = None
    print(f"Context insights: {context.get('insights')}")
    print(f"Context predictions: {context.get('predictions')}")
    
    if context.get('insights') and 'monthly_patterns' in context['insights']:
        print("Generating seasonal trends chart")
        chart_data = generate_chart(
            context['insights']['monthly_patterns']['claim_count'],
            'seasonal_trends',
            f"Seasonal Trends - {context.get('detected_claim_type', 'Claims').replace('_', ' ').title()}",
            context.get('detected_county'),
            context.get('detected_claim_type')
        )
    elif context.get('predictions') and len(context['predictions']) > 1:
        print("Generating prediction timeline chart")
        chart_data = generate_chart(
            context['predictions'],
            'prediction_timeline',
            f"Prediction Timeline - {context.get('detected_county', '')} {context.get('detected_claim_type', '').replace('_', ' ').title()}"
        )
    else:
        print("No chart data available")
    
    system_prompt = """You are a Kansas health insurance claims prediction assistant. 
    Format your responses with clear structure using markdown-like formatting:
    - Use **bold** for key numbers and important points
    - Use bullet points for lists
    - Use headers with ## for main sections
    - Keep paragraphs short and readable
    - Always include specific numbers from the data provided
    - If a chart is provided, mention it in your response
    
    Available Kansas counties include Johnson, Sedgwick, Shawnee, Wyandotte, Douglas, and others.
    Claim types include: emergency, inpatient, outpatient, pharmacy, mental_health, preventive.
    """
    
    user_message = f"User question: {message}\n\n"
    
    if context.get('predictions'):
        user_message += f"Prediction data: {json.dumps(context['predictions'][:3])}\n"
    
    if context.get('insights'):
        user_message += f"Seasonal insights: {json.dumps(context['insights'])}\n"
    
    if context.get('detected_county'):
        user_message += f"Detected county: {context['detected_county']}\n"
    
    if context.get('detected_claim_type'):
        user_message += f"Detected claim type: {context['detected_claim_type']}\n"
    
    if chart_data:
        user_message += "\nA chart has been generated to visualize this data.\n"
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = format_response_text(chat_completion.choices[0].message.content)
        
        # Add chart to response if generated
        if chart_data:
            print("Adding chart to response")
            response_text += f"\n\n![Chart]({chart_data})"
        else:
            print("No chart data to add")
        
        return response_text
    
    except Exception as e:
        return f"I'm having trouble processing your request right now. Error: {str(e)}"

def generate_fallback_response(message: str, context: dict):
    """Generate a formatted fallback response when Groq is not available"""
    if context.get('detected_county') and context.get('detected_claim_type'):
        county = context['detected_county']
        claim_type = context['detected_claim_type'].replace('_', ' ')
        
        if context.get('predictions'):
            pred = context['predictions'][0]
            response = f"## {county} County {claim_type.title()} Claims Prediction\n\n"
            response += f"**Predicted Volume:** {pred['predicted_count']} claims\n"
            response += f"**Estimated Cost:** ${pred['predicted_cost']:,.2f}\n"
            response += f"**Average Cost per Claim:** ${pred['avg_cost_per_claim']:,.2f}\n\n"
            
            if context.get('insights'):
                insights = context['insights']
                if 'monthly_patterns' in insights:
                    monthly = insights['monthly_patterns']['claim_count']
                    peak_month = max(monthly.items(), key=lambda x: x[1])
                    response += f"**Seasonal Pattern:** Peak month is {peak_month[0]} with {peak_month[1]:.0f} average claims\n"
            
            return response
        else:
            return f"## {county} County Analysis\n\nI found information about **{claim_type}** claims in **{county} County**. Please check if the data is available for this combination."
    else:
        return "## Kansas Healthcare Claims Predictor\n\nI can help you with Kansas healthcare claims predictions.\n\n**Available Counties:** Johnson, Sedgwick, Shawnee, Wyandotte, Douglas, and others\n**Claim Types:** emergency, pharmacy, mental health, inpatient, outpatient, preventive\n\nPlease specify a county and claim type for predictions."

def format_response_text(text: str) -> str:
    """Format response text for better readability"""
    # Add proper spacing and formatting
    formatted = text.replace('\n\n', '\n\n')
    formatted = formatted.replace('**', '**')
    return formatted

async def stream_response(text: str):
    """Stream response text character by character to simulate typing"""
    import asyncio
    
    for char in text:
        yield char
        # Add small delay to simulate typing (adjust speed as needed)
        await asyncio.sleep(0.02)  # 20ms delay per character

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)