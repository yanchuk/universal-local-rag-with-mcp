#!/usr/bin/env python3
"""
Universal Interview Preparation Tool
Interactive interview practice using your organization's knowledge base
Configurable for any organization and role
"""

import yaml
import chromadb
import sys
import random
from typing import Dict, List, Any
from pathlib import Path

class UniversalInterviewPrep:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self.load_config(config_path)
        if not self.config:
            sys.exit(1)
        
        self.org_name = self.config['organization']['name']
        self.client = None
        self.collection = None
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return None
    
    def get_collection_name(self) -> str:
        """Get collection name from config"""
        org_name = self.org_name.lower().replace(' ', '_')
        base_name = self.config['chromadb']['collection_name']
        return f"{org_name}_{base_name}"
    
    def connect_to_knowledge_base(self):
        """Connect to ChromaDB and access the knowledge collection"""
        try:
            chromadb_config = self.config['chromadb']
            self.client = chromadb.HttpClient(
                host=chromadb_config.get('host', 'localhost'),
                port=chromadb_config.get('port', 8000)
            )
            
            collection_name = self.get_collection_name()
            self.collection = self.client.get_collection(collection_name)
            count = self.collection.count()
            
            print(f"✅ Connected to {self.org_name} knowledge base")
            print(f"📊 {count} documents available for interview preparation")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to knowledge base: {e}")
            print("   Make sure ChromaDB is running and you've completed the setup process")
            return False
    
    def generate_interview_questions(self) -> List[Dict[str, str]]:
        """Generate interview questions based on configuration"""
        questions = []
        
        rag_goals = self.config['rag_goals']
        focus_areas = rag_goals.get('focus_areas', [])
        primary_purpose = rag_goals.get('primary_purpose', 'knowledge_management')
        target_role = rag_goals.get('target_role', 'general')
        target_teams = self.config.get('target_teams', [])
        
        # Universal organizational questions
        questions.extend([
            {
                "question": f"What can you tell me about {self.org_name}'s culture and values?",
                "category": "Company Culture",
                "query": f"{self.org_name} culture values mission principles"
            },
            {
                "question": f"How would you describe {self.org_name}'s organizational structure?",
                "category": "Organization",
                "query": f"{self.org_name} organization structure teams departments"
            },
            {
                "question": f"What do you know about how {self.org_name} operates?",
                "category": "Operations",
                "query": f"{self.org_name} processes operations workflow"
            }
        ])
        
        # Focus area specific questions
        if 'company_culture' in focus_areas:
            questions.extend([
                {
                    "question": f"How do you think {self.org_name}'s values would influence your daily work?",
                    "category": "Culture Fit",
                    "query": f"{self.org_name} values decision making culture daily work"
                },
                {
                    "question": f"What attracts you to {self.org_name}'s mission and approach?",
                    "category": "Mission Alignment",
                    "query": f"{self.org_name} mission vision purpose why exists"
                }
            ])
        
        if 'team_dynamics' in focus_areas:
            questions.extend([
                {
                    "question": f"How do you see yourself collaborating with teams at {self.org_name}?",
                    "category": "Team Collaboration", 
                    "query": f"{self.org_name} team collaboration cross-functional work together"
                },
                {
                    "question": f"What do you know about how teams are structured at {self.org_name}?",
                    "category": "Team Structure",
                    "query": f"{self.org_name} team structure organization responsibilities"
                }
            ])
        
        if 'customer_insights' in focus_areas:
            questions.extend([
                {
                    "question": f"What do you understand about {self.org_name}'s customers and their needs?",
                    "category": "Customer Understanding",
                    "query": f"{self.org_name} customers users problems needs pain points"
                },
                {
                    "question": f"How would you approach understanding customer problems at {self.org_name}?",
                    "category": "Customer Focus",
                    "query": f"{self.org_name} customer feedback research user experience"
                }
            ])
        
        if 'product_strategy' in focus_areas:
            questions.extend([
                {
                    "question": f"What do you know about {self.org_name}'s product strategy and direction?",
                    "category": "Product Strategy",
                    "query": f"{self.org_name} product strategy roadmap vision direction"
                },
                {
                    "question": f"How do you think {self.org_name} prioritizes features and initiatives?",
                    "category": "Prioritization",
                    "query": f"{self.org_name} prioritization decision making product features"
                }
            ])
        
        # Role-specific questions
        if target_role == 'product_manager':
            questions.extend([
                {
                    "question": f"How would you approach product decisions at {self.org_name}?",
                    "category": "Product Management",
                    "query": f"{self.org_name} product decisions framework process"
                },
                {
                    "question": f"What do you see as the biggest product challenges at {self.org_name}?",
                    "category": "Product Challenges",
                    "query": f"{self.org_name} product challenges problems priorities"
                }
            ])
        elif target_role == 'engineer':
            questions.extend([
                {
                    "question": f"What do you know about {self.org_name}'s technical architecture and approach?",
                    "category": "Technical Architecture",
                    "query": f"{self.org_name} technical architecture engineering practices"
                },
                {
                    "question": f"How does {self.org_name} approach technical decision-making?",
                    "category": "Technical Decisions",
                    "query": f"{self.org_name} technical decisions engineering process"
                }
            ])
        
        # Team-specific questions
        for team in target_teams[:3]:  # Focus on first 3 teams
            team_name = team['name']
            questions.append({
                "question": f"What do you know about the {team_name} team at {self.org_name}?",
                "category": f"{team_name.title()} Team",
                "query": f"{self.org_name} {team_name} team responsibilities work objectives"
            })
        
        return questions
    
    def search_knowledge_base(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        try:
            # Search with filters for goal-relevant content
            results = self.collection.query(
                query_texts=[query],
                where={"is_goal_relevant": True},
                n_results=3
            )
            
            if not results['documents'] or not results['documents'][0]:
                # Fallback search without filters
                results = self.collection.query(
                    query_texts=[query],
                    n_results=3
                )
            
            insights = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    insights.append({
                        'content': doc,
                        'metadata': metadata,
                        'relevance_rank': i + 1
                    })
            
            return insights
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def practice_interview_question(self, question_data: Dict[str, str]):
        """Practice a single interview question with knowledge base support"""
        question = question_data['question']
        category = question_data['category']
        query = question_data['query']
        
        print(f"\n📋 {category}")
        print("=" * 60)
        print(f"❓ {question}")
        print("")
        
        # Get user response
        print("💭 Take a moment to think about your answer...")
        input("   Press Enter when you're ready to see relevant information from the knowledge base...")
        
        # Search knowledge base
        print("\n🔍 Searching knowledge base for relevant information...")
        insights = self.search_knowledge_base(query, category)
        
        if insights:
            print(f"\n📚 Found {len(insights)} relevant insights:")
            for i, insight in enumerate(insights):
                metadata = insight['metadata']
                content_type = metadata.get('content_type', 'unknown')
                content_category = metadata.get('content_category', 'unknown')
                title = metadata.get('title', 'No title')
                is_relevant = metadata.get('is_goal_relevant', False)
                
                relevance_icon = "🎯" if is_relevant else "📄"
                print(f"\n  {i+1}. {relevance_icon} [{content_type}|{content_category}] {title}")
                print(f"     {insight['content'][:300]}...")
                
                if len(insight['content']) > 300:
                    show_more = input("     Show full content? (y/N): ").lower().strip()
                    if show_more == 'y':
                        print(f"\n     Full content:\n     {insight['content']}")
        else:
            print(f"\n⚠️  No specific information found for this question.")
            print(f"   This might be a good opportunity to ask about this topic during your interview!")
        
        print(f"\n💡 Discussion points to consider:")
        print(f"   • How does this information relate to the role you're applying for?")
        print(f"   • What questions does this raise that you'd like to ask your interviewer?")
        print(f"   • How would you apply this knowledge in your potential role?")
        
        input("\n   Press Enter to continue to the next question...")
    
    def run_interview_practice(self):
        """Run the complete interview practice session"""
        
        print(f"🎤 {self.org_name} Interview Preparation")
        print("=" * 60)
        print(f"🎯 Purpose: {self.config['rag_goals'].get('primary_purpose', 'knowledge_management')}")
        print(f"📋 Focus areas: {', '.join(self.config['rag_goals'].get('focus_areas', []))}")
        
        if not self.connect_to_knowledge_base():
            return
        
        print(f"\n🚀 Generating interview questions for {self.org_name}...")
        questions = self.generate_interview_questions()
        
        print(f"\n📝 Generated {len(questions)} interview questions")
        print(f"   Categories: {', '.join(set(q['category'] for q in questions))}")
        
        # Ask user how many questions they want to practice
        print(f"\nHow many questions would you like to practice?")
        print(f"1. Quick practice (5 questions)")
        print(f"2. Standard practice (10 questions)")
        print(f"3. Comprehensive practice (all {len(questions)} questions)")
        print(f"4. Custom number")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            num_questions = min(5, len(questions))
        elif choice == '2':
            num_questions = min(10, len(questions))
        elif choice == '3':
            num_questions = len(questions)
        elif choice == '4':
            try:
                num_questions = int(input(f"Enter number of questions (1-{len(questions)}): "))
                num_questions = max(1, min(num_questions, len(questions)))
            except ValueError:
                num_questions = 5
        else:
            num_questions = 5
        
        # Select questions (randomize for variety)
        selected_questions = random.sample(questions, num_questions)
        
        print(f"\n🎯 Starting interview practice with {num_questions} questions...")
        print(f"📚 Using {self.org_name} knowledge base for insights")
        print(f"\n💡 Tip: Think about your answers before looking at the knowledge base insights!")
        
        input("\nPress Enter to start...")
        
        # Practice each question
        for i, question_data in enumerate(selected_questions):
            print(f"\n{'='*60}")
            print(f"Question {i+1} of {num_questions}")
            self.practice_interview_question(question_data)
        
        # Final summary
        print(f"\n🎉 Interview Practice Complete!")
        print("=" * 60)
        print(f"✅ Practiced {num_questions} questions about {self.org_name}")
        print(f"📚 Used knowledge base insights for better preparation")
        
        print(f"\n💡 Next steps:")
        print(f"   • Review the insights you found most surprising or useful")
        print(f"   • Prepare follow-up questions based on what you learned")
        print(f"   • Practice articulating how you'd apply this knowledge in the role")
        print(f"   • Research areas where you found limited information")
        
        print(f"\n🔄 Run this tool again anytime to practice with different questions!")

def main():
    """Main function"""
    
    # Get config file from command line argument
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    if not Path(config_path).exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("   Please create a config.yaml file or specify a different config file")
        print("   Example: python scripts/interview_prep.py config_examples/startup_company.yaml")
        sys.exit(1)
    
    # Create and run interview prep
    interview_prep = UniversalInterviewPrep(config_path)
    interview_prep.run_interview_practice()

if __name__ == "__main__":
    main()
