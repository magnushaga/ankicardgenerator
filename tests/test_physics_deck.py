from flask import Flask
import json
import uuid
from datetime import datetime
from models_with_states import db, User, Textbook, Deck, Part, Chapter, Topic, Card, UserCardState

def create_test_user():
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="test_user"
    )
    user.set_password("test123")
    return user

def create_physics_cards(topic_title):
    """Create realistic physics cards based on the topic"""
    cards_data = {
        "Linear Motion": [
            {
                "front": "What is the difference between distance and displacement?",
                "back": "Distance is a scalar quantity measuring the total path length traveled, while displacement is a vector quantity measuring the straight-line distance and direction from start to end point."
            },
            {
                "front": "Define acceleration and give its SI unit.",
                "back": "Acceleration is the rate of change of velocity with respect to time. SI unit: meters per second squared (m/s²)"
            },
            {
                "front": "What is the equation for average velocity?",
                "back": "v_avg = Δx/Δt\nwhere Δx is displacement and Δt is time interval"
            },
            {
                "front": "State the equation for displacement under constant acceleration.",
                "back": "x = x₀ + v₀t + ½at²\nwhere:\nx₀ = initial position\nv₀ = initial velocity\nt = time\na = acceleration"
            },
            {
                "front": "What is instantaneous velocity?",
                "back": "Instantaneous velocity is the velocity of an object at a specific point in time. Mathematically, it's the derivative of position with respect to time: v = dx/dt"
            }
        ],
        "Projectile Motion": [
            {
                "front": "What are the two independent components of projectile motion?",
                "back": "1. Horizontal motion (constant velocity)\n2. Vertical motion (constant acceleration due to gravity)"
            },
            {
                "front": "Write the equations for the x and y positions of a projectile.",
                "back": "x = x₀ + v₀cosθ·t\ny = y₀ + v₀sinθ·t - ½gt²\nwhere:\nv₀ = initial velocity\nθ = launch angle\ng = acceleration due to gravity"
            },
            {
                "front": "What is the trajectory shape of an ideal projectile?",
                "back": "A parabola (neglecting air resistance)"
            },
            {
                "front": "For maximum range, what should be the launch angle?",
                "back": "45 degrees (in the absence of air resistance and assuming same initial and final heights)"
            },
            {
                "front": "What factors affect the range of a projectile?",
                "back": "1. Initial velocity\n2. Launch angle\n3. Initial height\n4. Air resistance\n5. Gravitational acceleration"
            }
        ],
        "Newton's Laws": [
            {
                "front": "State Newton's First Law of Motion.",
                "back": "An object remains at rest or in uniform motion in a straight line unless acted upon by an external force. Also known as the Law of Inertia."
            },
            {
                "front": "What is Newton's Second Law of Motion? Write the equation.",
                "back": "The acceleration of an object is directly proportional to the net force acting on it and inversely proportional to its mass.\nF = ma\nwhere:\nF = net force\nm = mass\na = acceleration"
            },
            {
                "front": "State Newton's Third Law of Motion.",
                "back": "For every action, there is an equal and opposite reaction. Forces always occur in pairs."
            },
            {
                "front": "What is the difference between mass and weight?",
                "back": "Mass is a measure of the amount of matter (kg)\nWeight is the gravitational force acting on mass (N)\nWeight = mass × gravitational acceleration"
            },
            {
                "front": "What is inertia and how is it related to mass?",
                "back": "Inertia is an object's resistance to change in its state of motion. Mass is a quantitative measure of inertia."
            }
        ],
        "Forces": [
            {
                "front": "What are the four fundamental forces in nature?",
                "back": "1. Gravitational force\n2. Electromagnetic force\n3. Strong nuclear force\n4. Weak nuclear force"
            },
            {
                "front": "Define normal force and when does it occur?",
                "back": "Normal force is the perpendicular force exerted by a surface on an object in contact with it. It occurs when two surfaces are in contact."
            },
            {
                "front": "What is friction? List its types.",
                "back": "Friction is the force resisting relative motion between surfaces in contact.\nTypes:\n1. Static friction\n2. Kinetic friction\n3. Rolling friction\n4. Fluid friction (drag)"
            },
            {
                "front": "Write the equation for gravitational force between two masses.",
                "back": "F = G(m₁m₂)/r²\nwhere:\nG = gravitational constant\nm₁,m₂ = masses\nr = distance between centers"
            },
            {
                "front": "What is tension? When is it important?",
                "back": "Tension is the pulling force transmitted through a string, rope, cable, or wire. Important in problems involving pulleys, suspended objects, and tethered motion."
            }
        ],
        "Temperature and Heat": [
            {
                "front": "What is the difference between heat and temperature?",
                "back": "Temperature is a measure of average kinetic energy of particles in a substance.\nHeat is the transfer of thermal energy between objects due to temperature difference."
            },
            {
                "front": "Write the equation for temperature conversion between Celsius and Fahrenheit.",
                "back": "°F = (°C × 9/5) + 32\n°C = (°F - 32) × 5/9"
            },
            {
                "front": "What is specific heat capacity? Write its equation.",
                "back": "Specific heat capacity is the amount of heat needed to raise the temperature of 1 kg of a substance by 1 K.\nQ = mcΔT\nwhere:\nQ = heat energy\nm = mass\nc = specific heat capacity\nΔT = temperature change"
            },
            {
                "front": "Define thermal equilibrium.",
                "back": "Thermal equilibrium is the state where two objects have reached the same temperature and no net heat transfer occurs between them."
            },
            {
                "front": "What is latent heat? Give examples.",
                "back": "Latent heat is the heat required to change the phase of a substance without changing its temperature.\nExamples:\n1. Latent heat of fusion (solid to liquid)\n2. Latent heat of vaporization (liquid to gas)"
            }
        ],
        "Heat Transfer": [
            {
                "front": "What are the three methods of heat transfer?",
                "back": "1. Conduction (through direct contact)\n2. Convection (through fluid motion)\n3. Radiation (through electromagnetic waves)"
            },
            {
                "front": "Write the equation for conductive heat transfer.",
                "back": "Q/t = -kA(ΔT/Δx)\nwhere:\nQ/t = heat transfer rate\nk = thermal conductivity\nA = cross-sectional area\nΔT = temperature difference\nΔx = thickness"
            },
            {
                "front": "Explain convection current.",
                "back": "Convection currents occur when fluid is heated:\n1. Fluid becomes less dense when heated\n2. Less dense fluid rises\n3. Cooler fluid sinks\n4. Creates a circular motion"
            },
            {
                "front": "What is the Stefan-Boltzmann law for radiation?",
                "back": "P = εσAT⁴\nwhere:\nP = power radiated\nε = emissivity\nσ = Stefan-Boltzmann constant\nA = surface area\nT = absolute temperature"
            },
            {
                "front": "What is thermal resistance? How is it calculated?",
                "back": "Thermal resistance (R) is the ability of a material to resist heat flow.\nR = L/kA\nwhere:\nL = thickness\nk = thermal conductivity\nA = cross-sectional area"
            }
        ],
        "First Law": [
            {
                "front": "State the First Law of Thermodynamics.",
                "back": "Energy cannot be created or destroyed, only converted from one form to another. ΔU = Q - W\nwhere:\nΔU = change in internal energy\nQ = heat added to system\nW = work done by system"
            },
            {
                "front": "What is internal energy?",
                "back": "Internal energy is the total kinetic and potential energy of all particles in a system. It includes:\n1. Kinetic energy of molecular motion\n2. Potential energy of molecular interactions"
            },
            {
                "front": "Define work in thermodynamics.",
                "back": "Work in thermodynamics is the energy transfer due to a change in volume against pressure.\nW = PΔV\nwhere:\nP = pressure\nΔV = change in volume"
            },
            {
                "front": "What is an adiabatic process?",
                "back": "An adiabatic process is one where no heat transfer occurs between the system and surroundings (Q = 0).\nCommon in rapid compression or expansion."
            },
            {
                "front": "What is the sign convention in thermodynamics?",
                "back": "1. Q > 0: Heat added to system\n2. Q < 0: Heat removed from system\n3. W > 0: Work done by system\n4. W < 0: Work done on system"
            }
        ],
        "Second Law": [
            {
                "front": "State the Second Law of Thermodynamics.",
                "back": "Heat flows spontaneously from hot to cold objects, not vice versa. The total entropy of an isolated system always increases."
            },
            {
                "front": "What is entropy? How is it calculated?",
                "back": "Entropy is a measure of disorder or randomness in a system.\nΔS = Q/T (for reversible processes)\nwhere:\nΔS = change in entropy\nQ = heat transfer\nT = absolute temperature"
            },
            {
                "front": "What is the Carnot efficiency?",
                "back": "η = 1 - Tc/Th\nwhere:\nη = maximum possible efficiency\nTc = cold reservoir temperature\nTh = hot reservoir temperature"
            },
            {
                "front": "Why are perpetual motion machines impossible?",
                "back": "They violate either:\n1. First Law (energy conservation)\n2. Second Law (entropy increase)\nNo machine can be 100% efficient due to inevitable energy dissipation."
            },
            {
                "front": "What is the relationship between entropy and disorder?",
                "back": "1. Higher entropy = more disorder\n2. Natural processes tend toward higher entropy\n3. Perfect crystals at 0K have minimum entropy\n4. Gases have higher entropy than liquids or solids"
            }
        ]
    }
    
    return cards_data.get(topic_title, [])

def setup_test_app():
    """Create and configure the test Flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_flashcards.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def create_physics_deck():
    """Create a complete physics deck with realistic cards"""
    app = setup_test_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create test user
        user = create_test_user()
        db.session.add(user)
        db.session.flush()
        
        # Create textbook
        textbook = Textbook(
            user_id=user.id,
            title="Fundamentals of Physics",
            author="Test Author",
            subject="Physics",
            description="A comprehensive introduction to physics covering mechanics and thermodynamics",
            tags=["physics", "mechanics", "thermodynamics"],
            difficulty_level="intermediate"
        )
        db.session.add(textbook)
        db.session.flush()
        
        # Create main deck
        deck = Deck(
            owner_id=user.id,
            name="Physics Fundamentals",
            description="Main deck for Physics fundamentals",
            textbook_id=textbook.id
        )
        db.session.add(deck)
        db.session.flush()
        
        # Create structure
        parts_data = [
            {
                "title": "Part 1: Classical Mechanics",
                "chapters": [
                    {
                        "title": "Chapter 1: Kinematics",
                        "topics": ["Linear Motion", "Projectile Motion"]
                    },
                    {
                        "title": "Chapter 2: Dynamics",
                        "topics": ["Newton's Laws", "Forces"]
                    }
                ]
            },
            {
                "title": "Part 2: Thermodynamics",
                "chapters": [
                    {
                        "title": "Chapter 3: Heat",
                        "topics": ["Temperature and Heat", "Heat Transfer"]
                    },
                    {
                        "title": "Chapter 4: Laws of Thermodynamics",
                        "topics": ["First Law", "Second Law"]
                    }
                ]
            }
        ]
        
        # Create parts, chapters, and topics with cards
        for part_idx, part_data in enumerate(parts_data):
            part = Part(
                deck_id=deck.id,
                title=part_data['title'],
                order_index=part_idx
            )
            db.session.add(part)
            db.session.flush()
            
            for chapter_idx, chapter_data in enumerate(part_data['chapters']):
                chapter = Chapter(
                    part_id=part.id,
                    title=chapter_data['title'],
                    order_index=chapter_idx
                )
                db.session.add(chapter)
                db.session.flush()
                
                for topic_idx, topic_title in enumerate(chapter_data['topics']):
                    topic = Topic(
                        chapter_id=chapter.id,
                        title=topic_title,
                        order_index=topic_idx
                    )
                    db.session.add(topic)
                    db.session.flush()
                    
                    # Create cards for this topic
                    cards_data = create_physics_cards(topic_title)
                    for card_data in cards_data:
                        card = Card(
                            deck_id=deck.id,
                            topic_id=topic.id,
                            front=card_data['front'],
                            back=card_data['back']
                        )
                        db.session.add(card)
                        db.session.flush()
                        
                        # Create card state
                        card_state = UserCardState(
                            user_id=user.id,
                            card_id=card.id,
                            is_active=True
                        )
                        db.session.add(card_state)
        
        db.session.commit()
        
        print("\n=== Physics Deck Created Successfully ===")
        print(f"User ID: {user.id}")
        print(f"Textbook: {textbook.title}")
        print(f"Deck: {deck.name}")
        
        # Print some statistics
        cards = Card.query.filter_by(deck_id=deck.id).all()
        topics = Topic.query.join(Chapter).join(Part).filter(Part.deck_id == deck.id).all()
        
        print(f"\nTotal cards created: {len(cards)}")
        print(f"Total topics: {len(topics)}")
        print("\nTopics and their cards:")
        for topic in topics:
            topic_cards = Card.query.filter_by(topic_id=topic.id).all()
            print(f"\n{topic.title}: {len(topic_cards)} cards")
            # Print first card as example
            if topic_cards:
                print("Example card:")
                print(f"Q: {topic_cards[0].front}")
                print(f"A: {topic_cards[0].back}")

if __name__ == '__main__':
    create_physics_deck()