# Star Jeans - Product Market Fit 

## ETL design to help define a new company's product market fit

<img src="/img/jason-leung-DmD8HVOjy4c-unsplash.jpg"
  alt="Alt text"
  title="cover image"
  style="display: inline-block; margin: 0 auto; max-width: 600px;height:600px">

*This project was proposed in the study trail of the Meigarom Lopes Data Science Community*

# 1. Business Problem.

Two Brazilians, partners in some ventures, decided to enter the US fashion market, building their own e-commerce called Star Jeans.

Considering the market risks, they planned to start their operation with just one product, in this case jeans, and scale the business as the company grows, which makes it possible to work with a low initial cost.

Therefore, they hired a data science consultancy to answer the following questions:

- What is the best selling price for the pants?
- How many types of pants and their colors for the initial product?
- What are the raw materials needed to make the pants?
- The main competitors of the company Start Jeans are the American H&M and Macys.

# 2. Business Assumptions
- At a section of e-commerce, the first showcase that appears is the best ranked and the one with the best selling products
- More frequent colors and types of pants have greater acceptance by the public and greater appeal for price

# 3. Solution Strategy

The solution strategy is based on a market research of H&M (initially), given that it is the main competitor at this segment. Through a ETL process, the data will be collected from H&M e-commerce and will ne used to adress the business problem. 

## 3.1. Delivable

The delivery of the project will be a dashboard that will contain:

1. Graphs of the main attributes (price, color, type and raw material)

2. Aswers to business questions

- How many types of pants and their colors for the initial product?<br>
  A: The two types of pants and colors + frequent in the data set will be recommended

- What is the best selling price for the pants? <br>
  A: 15% less than the median price of pants types and colors + frequent

- What are the raw materials needed to make the pants?<br>
  A: Raw materials of these most frequent pants

## 3.2. Process

- Definition of attributes to be extracted from the H&M website
- Definition of storage infrastructure (SQLITE3)
- ETL Design (Extraction, Transformation and Load Scripts)
- Scheduling planning of scripts (dependencies between scripts)
- Make the visualizations
- Delivery of the final product

## 3.3. Resources

**Data Source to scrap:**<br>
  
  H&M Website: https://www2.hm.com/en_us/men/products/jeans.html<br>
  The data used to answer the questions were drawn from the first window of the H&M men's jeans session, drawn over a month.

**Tools:**<br>

  - Python 3.10.9
  - Webscrapping Libraries (Beautiful Soup)
  - Jupyter Notebook (Analysis and Prototyping)
  - Crontjob
  - PowerBI
  
  
# 4. Business Results

# 5. Conclusions

# 6. Lessons Learned

# 7. Next Steps to Improve
