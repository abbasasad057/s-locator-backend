from all_types.request_dtypes import Dict, ReqFetchDataset
from preloaded_constants import GOOGLE_CATEGORIES


from fastapi import HTTPException, status
from fuzzywuzzy import fuzz, process


import re
from typing import Dict, Optional


def determine_data_type(
    req: ReqFetchDataset, categories: Dict
) -> Optional[str]:
    """
    Determines the data type based on boolean query.
    Returns:
    - Special category if ALL terms belong to that category
    - "google_categories" if ANY terms are Google or custom terms
    - Raises HTTPException if any terms are not in approved categories (with fuzzy suggestions)
    - Raises HTTPException if mixing Google/custom with special categories
    """
    boolean_query = req.boolean_query

    if not boolean_query:
        return None

    # check if text search is in the boolean query. indicated by @ sign wrapping the search term like @auto parts@ OR @car repair@ OR قطع غيار السيارات NOT بنشر
    # if so remove it from the boolean query and add it to the text search text_search_terms
    text_search_terms = re.findall(r"@([^@]+)@", boolean_query)
    for term in text_search_terms:
        boolean_query = boolean_query.replace(f"@{term}@", f"{term}")

    # Extract just the terms
    terms = set(
        term.strip()
        for term in boolean_query.replace("(", " ")
        .replace(")", " ")
        .replace("AND", " ")
        .replace("OR", " ")
        .replace("NOT", " ")
        .split()
    )

    if not terms:
        return None

    if req.search_type == "keyword_search":
        # If the search type is text_search, we can assume it's a Google search
        # and return the google_categories directly
        return "google_categories"

    # Create a set of all approved terms from all categories and organize by category
    approved_terms = set()
    categories_with_terms = {}

    for category_name, category_terms in categories.items():
        if isinstance(category_terms, list):
            approved_terms.update(category_terms)
            categories_with_terms[category_name] = category_terms

    # Check if all terms are in the approved list
    invalid_terms = terms - approved_terms
    if invalid_terms:
        # Generate fuzzy suggestions for each invalid term
        suggestions = {}
        for invalid_term in invalid_terms:
            # Get top 1 closest match
            closest_match = process.extractOne(
                invalid_term, list(approved_terms), scorer=fuzz.ratio
            )

            # Only suggest if score > 60 to avoid poor suggestions
            if closest_match and closest_match[1] > 60:
                suggestions[invalid_term] = {"did_you_mean": closest_match[0]}
            else:
                suggestions[invalid_term] = {"message": "No close match found"}

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Invalid terms found in boolean query",
                "invalid_terms": list(invalid_terms),
                "suggestions": suggestions,
                "help": "Use terms from the approved categories list below or try the suggested alternatives",
                "available_categories": categories_with_terms,
                "total_available_terms": len(approved_terms),
            },
        )

    # Check non-Google categories first
    for category, category_terms in categories.items():
        if category not in GOOGLE_CATEGORIES:
            matches = terms.intersection(set(category_terms))
            if matches:
                # If we found any special category terms, ALL terms must belong to this category
                if len(matches) != len(terms):
                    non_matching_terms = terms - matches

                    # Generate suggestions for non-matching terms within this category
                    category_suggestions = {}
                    for term in non_matching_terms:
                        closest_in_category = process.extractOne(
                            term, category_terms, scorer=fuzz.ratio
                        )

                        if closest_in_category and closest_in_category[1] > 60:
                            category_suggestions[term] = {
                                "did_you_mean": closest_in_category[0]
                            }
                        else:
                            category_suggestions[term] = {
                                "message": f"No close match in {category} category"
                            }

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "message": f"Cannot mix {category} terms with other category terms",
                            "category": category,
                            "valid_category_terms": list(matches),
                            "invalid_mixed_terms": list(non_matching_terms),
                            "suggestions": category_suggestions,
                            "suggestion": f"Use only {category} terms or only general/Google category terms",
                            "available_categories": categories_with_terms,
                        },
                    )
                return category

    # If we get here, no special category matches were found
    # So we can safely return google_categories for either Google terms or custom terms
    return "google_categories"