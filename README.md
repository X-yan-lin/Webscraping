# Scraping Marketing Information from E-Commerce Websites

## Project Background  
This project was developed to extract marketing-relevant product information from e-commerce websites, focusing on both list pages (which display multiple products) and product pages (dedicated to a single product). The goal is to support analysis of how product presentation varies across contexts.

## Methodology  
A single list page URL ('https://goodr.com/collections/best-sellers') was used to collect data on the first 10 products listed. The scraper gathered basic product details directly from the list page, and then visited corresponding product pages to extract additional information.

## About the Files  
The output is organized in a CSV file with the following fields:  
`URL`, `Page Type (list/product)`, `Product Name`, `Brand`, `Price`, `Discounted Price`, `Position`, `Number of Photos`, `Number of Colors`, `Product Description`.  

Scripts include functions for scraping both page types and structuring the output data accordingly.
