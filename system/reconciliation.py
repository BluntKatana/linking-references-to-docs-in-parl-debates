import re
from system.utils.obm import get_obm_document_info
from vectordb.query import query_vector_database
from utils.file import save_results
from featurebuilder import FeatureBuilder

def reconcile_references(minute_id: str, enhanced_references: str, featurebuilder: FeatureBuilder):
    """
    Links the enhanced references to dossiers and documents in the database.

    Args:
        enhanced_references: The list of enhanced references
        minute_id: The identifier of the minute
        linking_system: LinkingSystem instance defining query and filter configuration

    Returns:
        A list of linked references with ranked candidates and their reference IDs
    """
    # Retrieve the minute details
    minute = get_obm_document_info(minute_id)

    linked_references = []

    for reference in enhanced_references:
        # If the reference is explicit, we can try to directly link to it from the referenced
        # document, otherwise we need to still search for it
        explicit_types = ['explicit-parl-doc', 'explicit-dossier']
        reference_type = reference['reference_type']
        if reference_type in explicit_types:
            text = reference.get('reference_text', '')
            correct_reference = pattern_match_identifier_from_text(text)
            if correct_reference:
                reference["found_direct"] = correct_reference

        doc_type = reference.get('document_type', None)

        # Build query using the linking system
        query_text = featurebuilder.build_query(reference)

        # Get filters from the linking system
        filters = featurebuilder.get_filters(minute.get('date', None), doc_type)

        # Search for candidates
        candidates = query_vector_database(
            query_text,
            year=filters.get('year'),
            doc_type=filters.get('doc_type')
        )

        # Sort candidates by similarity_score
        candidates = sorted(candidates, key=lambda x: x.get('similarity_score', 0), reverse=True)

        # Add the ranked candidates to the reference
        reference["query"] = query_text
        reference["ranked_candidates"] = candidates
        linked_references.append(reference)

    # Save the linked references
    save_results(linked_references, minute.get('identifier', 'unknown'), featurebuilder.name)

    return linked_references


def pattern_match_identifier_from_text(text):
    """
    Extracts a reference ID from text, always returning either:
    - dossier number (e.g., "34834")
    - dossier-document number (e.g., "34834-9")
    """
    text = text.strip()
    if not text:
        return None

    # First try to find dossier-document patterns
    dossier_doc_patterns = [
        # Standard format: 25424-430
        r'(\d{5})-(\d{1,4})',

        # Budget format: 35000-A-28 -> convert to 35000A-28
        r'(\d{5})-([A-Z])-(\d{1,4})',

        # Format: 34834, nr. 9
        r'(\d{5}),\s*nr\.\s*(\d{1,4})',

        # Format: nr. 17, was nr. 9 (34834)
        r'nr\.\s*(\d{1,4})(?:,\s*was\s*nr\.\s*\d+)?\s*\((\d{5})\)'
    ]

    for pattern in dossier_doc_patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                dossier, doc = match.groups()
                return f"{dossier}-{doc}"
            elif len(match.groups()) == 3:  # Budget format
                dossier, letter, doc = match.groups()
                return f"{dossier}-{letter}-{doc}"

    # If no dossier-doc pattern found, look for just dossier numbers
    dossier_patterns = [
        # Just the dossier number
        r'(\d{5})\b',

        # Year-based references (e.g., 2018Z21641)
        r'(20\d{2}Z\d{5})'
    ]

    for pattern in dossier_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None