"""
File recipe parser - Extract recipes from HTML and PDF files.

Supports parsing HTML and PDF files to extract recipe information.
"""

import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import pdfplumber


class FileRecipeParser:
    """Parse recipe information from HTML and PDF files."""

    @staticmethod
    def parse_html_file(content: str) -> Dict[str, Any]:
        """
        Parse recipe from HTML file content.

        Args:
            content: HTML file content as string

        Returns:
            Dictionary with extracted recipe data
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Extract title - look for common patterns
            title = None
            if soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            elif soup.find('title'):
                title = soup.find('title').get_text(strip=True)

            # Extract ingredients
            ingredients = FileRecipeParser._extract_ingredients(soup)

            # Extract instructions
            instructions = FileRecipeParser._extract_instructions(soup)

            # Extract cooking times
            prep_time, cook_time = FileRecipeParser._extract_times(soup, content)

            # Extract servings
            servings = FileRecipeParser._extract_servings(soup, content)

            return {
                'title': title or 'Untitled Recipe',
                'ingredients': ingredients,
                'instructions': instructions,
                'prep_time': prep_time,
                'cook_time': cook_time,
                'servings': servings,
                'source_type': 'html',
            }
        except Exception as e:
            raise ValueError(f"Failed to parse HTML file: {str(e)}")

    @staticmethod
    def parse_pdf_file(file_path: str) -> Dict[str, Any]:
        """
        Parse recipe from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with extracted recipe data
        """
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                # Extract text from all pages
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

            # Parse as text-based recipe
            return FileRecipeParser._parse_text_recipe(text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF file: {str(e)}")

    @staticmethod
    def _extract_ingredients(soup: BeautifulSoup) -> list:
        """Extract ingredient list from HTML."""
        ingredients = []

        # Look for common ingredient container patterns
        ingredient_containers = [
            soup.find_all(class_=re.compile(r'ingredient', re.I)),
            soup.find_all('li', class_=re.compile(r'ingredient', re.I)),
            soup.find('div', class_=re.compile(r'ingredient', re.I)),
        ]

        for container in ingredient_containers:
            if container:
                for item in (container if isinstance(container, list) else [container]):
                    text = item.get_text(strip=True) if hasattr(item, 'get_text') else str(item)
                    if text and len(text) > 2:
                        ingredients.append(text)
                if ingredients:
                    break

        # Fallback: look for list items that look like ingredients
        if not ingredients:
            for li in soup.find_all('li'):
                text = li.get_text(strip=True)
                # Simple heuristic: ingredient-like text
                if any(word in text.lower() for word in ['cup', 'tbsp', 'tsp', 'oz', 'lb', 'gram', 'ml', 'g']):
                    ingredients.append(text)

        return ingredients[:20]  # Limit to 20 ingredients

    @staticmethod
    def _extract_instructions(soup: BeautifulSoup) -> str:
        """Extract instructions from HTML."""
        # Look for instructions container
        instruction_containers = soup.find_all(class_=re.compile(r'instruction|direction|step', re.I))

        if instruction_containers:
            steps = []
            for container in instruction_containers:
                text = container.get_text(strip=True)
                if text:
                    steps.append(text)
            return '\n'.join(steps)

        # Fallback: extract all paragraphs that look like instructions
        paragraphs = soup.find_all('p')
        instructions = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 20:  # Likely an instruction paragraph
                instructions.append(text)

        return '\n'.join(instructions[:10])  # Limit to 10 paragraphs

    @staticmethod
    def _extract_times(soup: BeautifulSoup, html_content: str) -> tuple:
        """Extract prep time and cook time from HTML."""
        prep_time = None
        cook_time = None

        # Look for time attributes or classes
        time_pattern = r'(\d+)\s*(?:minutes?|mins?|min)'

        # Search for prep time
        prep_match = re.search(r'prep(?:\s+)?time[:\s]+' + time_pattern, html_content, re.I)
        if prep_match:
            prep_time = int(prep_match.group(1))

        # Search for cook time
        cook_match = re.search(r'cook(?:\s+)?time[:\s]+' + time_pattern, html_content, re.I)
        if cook_match:
            cook_time = int(cook_match.group(1))

        return prep_time, cook_time

    @staticmethod
    def _extract_servings(soup: BeautifulSoup, html_content: str) -> Optional[int]:
        """Extract servings from HTML."""
        # Look for servings pattern
        servings_pattern = r'servings?[:\s]+(\d+)'
        match = re.search(servings_pattern, html_content, re.I)
        if match:
            return int(match.group(1))

        # Default
        return 4

    @staticmethod
    def _parse_text_recipe(text: str) -> Dict[str, Any]:
        """Parse recipe from plain text (used for PDF and text files)."""
        lines = text.split('\n')

        # Extract title (first non-empty line, usually)
        title = None
        for line in lines:
            line = line.strip()
            if line and len(line) < 100:  # Likely a title
                title = line
                break

        # Extract ingredients (look for "ingredients:" section)
        ingredients = []
        instructions = []
        in_ingredients = False
        in_instructions = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if re.search(r'^ingredients?:', line, re.I):
                in_ingredients = True
                in_instructions = False
                continue
            elif re.search(r'^instructions?:|directions?:|steps?:', line, re.I):
                in_ingredients = False
                in_instructions = True
                continue

            if in_ingredients and line:
                ingredients.append(line)
            elif in_instructions and line:
                instructions.append(line)

        # If we didn't find explicit sections, try to guess
        if not ingredients:
            for line in lines:
                line = line.strip()
                if any(unit in line.lower() for unit in ['cup', 'tbsp', 'tsp', 'oz', 'lb', 'g ', 'ml', 'gram']):
                    ingredients.append(line)

        return {
            'title': title or 'Untitled Recipe',
            'ingredients': ingredients[:20],
            'instructions': '\n'.join(instructions),
            'prep_time': None,
            'cook_time': None,
            'servings': 4,
            'source_type': 'file',
        }
