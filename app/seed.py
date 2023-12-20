'''This file is an initialization script, so that when the database tables are created for the first time, 
the restaurant menu is automatically persisted'''

from .models import Product
from .database import SessionLocal

# Function to insert the menu
def insert_initial_data():
    
    session = SessionLocal()
    
    # Checks if the menu has already been inserted
    if session.query(Product).count() == 0:
        
        # Restaurant menu, automatically inserted, when the first time the tables are initialized
        product_data = [
            ('Grilled Salmon', 'Freshly grilled salmon served with lemon butter sauce, accompanied by roasted vegetables and quinoa.', 20.99),
            ('Chicken Alfredo Pasta', 'Creamy Alfredo sauce with grilled chicken served over fettuccine pasta, garnished with parmesan cheese.', 16.99),
            ('Vegetarian Stir-Fry', 'Colorful stir-fried vegetables with tofu, served on a bed of steamed jasmine rice.', 14.99),
            ('Beef Tenderloin Steak', 'Juicy beef tenderloin steak cooked to perfection, served with mashed potatoes and sautéed spinach.', 28.99),
            ('Shrimp Scampi', 'Succulent shrimp sautéed in garlic butter and white wine, served over a bed of linguine pasta.', 22.99),
            ('Mushroom Risotto', 'Creamy mushroom risotto made with Arborio rice, topped with truffle oil and parmesan shavings.', 18.99),
            ('Pesto Chicken Salad', 'Grilled pesto-marinated chicken breast served on a bed of mixed greens with cherry tomatoes and balsamic vinaigrette.', 12.99),
            ('Eggplant Parmesan', 'Layers of breaded and baked eggplant with marinara sauce and melted mozzarella cheese, served with spaghetti.', 17.99),
            ('Teriyaki Glazed Tofu Bowl', 'Teriyaki glazed tofu served with stir-fried vegetables and brown rice.', 15.99),
            ('BBQ Pulled Pork Sandwich', 'Slow-cooked pulled pork in tangy barbecue sauce, served on a toasted brioche bun with coleslaw.', 13.99),
            ('Classic Mojito', 'Freshly muddled mint and lime, mixed with white rum and soda water.', 8.99),
            ('Berry Blast Smoothie', 'A refreshing blend of mixed berries, banana, yogurt, and a touch of honey.', 6.99),
            ('Iced Caramel Macchiato', 'Espresso poured over iced milk, sweetened with caramel syrup.', 4.99),
            ('Mango Tango Lemonade', 'Fresh mango puree combined with lemonade, served over ice.', 5.99),
            ('Classic Old Fashioned', 'A timeless cocktail made with bourbon, sugar, and bitters, garnished with an orange twist.', 10.99),
            ('Green Tea Matcha Latte', 'Steamed milk mixed with high-quality matcha green tea powder.', 5.99),
            ('Pineapple Coconut Cooler', 'Pineapple juice and coconut cream blended with ice for a tropical treat.', 7.99),
            ('Sparkling Raspberry Lemonade', 'Fizzy lemonade with a burst of raspberry flavor, served with crushed ice.', 4.99),
            ('Espresso Martini', 'A sophisticated mix of vodka, coffee liqueur, and freshly brewed espresso.', 12.99),
            ('Strawberry Basil Infused Water', 'Fresh strawberries and basil leaves infused in cold water for a refreshing non-alcoholic option.', 3.99),
            ('Chocolate Lava Cake', 'Warm chocolate cake with a gooey molten center, served with a scoop of vanilla ice cream.', 7.99),
            ('New York Cheesecake', 'Creamy cheesecake on a graham cracker crust, topped with a choice of fruit compote.', 6.99),
            ('Tiramisu', 'Classic Italian dessert with layers of coffee-soaked ladyfingers and mascarpone cream.', 8.99),
            ('Key Lime Pie', 'Tangy key lime filling in a buttery graham cracker crust, topped with whipped cream.', 5.99),
            ('Apple Crumble', 'Baked apple slices with cinnamon and brown sugar, topped with a crispy crumble and vanilla ice cream.', 6.99),
            ('Red Velvet Cupcake', 'Moist red velvet cupcake with cream cheese frosting and a sprinkle of chocolate shavings.', 4.99),
            ('Banoffee Pie', 'Banana and toffee filling in a buttery pie crust, topped with whipped cream.', 7.99),
            ('Lemon Sorbet', 'Refreshing lemon sorbet served in a hollowed-out lemon half.', 4.99),
            ('Chocolate Dipped Strawberries', 'Fresh strawberries dipped in rich dark chocolate.', 9.99),
            ('Panna Cotta with Raspberry Coulis', 'Silky vanilla panna cotta topped with a vibrant raspberry coulis.', 6.99)
        ]

        # Iterates over the data and insert it into the 'product' table
        for name, description, price in product_data:
            new_product = Product(name=name, description=description, price=price)
            session.add(new_product)

        # Commits Changes
        session.commit()
        # Closes Session
        session.close()