class FeatureBuilder:
    def __init__(self, name, query_fields=None, filters=None):
        """
        Initialize a reconciliation system configuration.

        Args:
            name: Name of the reconciliation system
            query_fields: List of fields to include in query vector (default: ['reference_text'])
            filters: Dict of filters to apply {'year': bool, 'doc_type': bool}
        """
        self.name = name
        self.query_fields = query_fields or ['reference_text']
        self.filters = filters or {}

    def build_query(self, reference):
        """Build query text from specified fields."""
        query_parts = []

        found_direct = reference.get('found_direct', None)

        for field in self.query_fields:
            if field == 'reference_text':
                text = reference.get('reference_text', '')
                # Remove reference text from query if found_direct exists
                if found_direct:
                    # remove any combination of dossier and document numbers
                    numbers = found_direct.split('-')
                    text = text.replace(found_direct, '')
                    for number in numbers:
                        text = text.replace(number, '')
                query_parts.append(text)
            elif field == 'sentence':
                sentence = reference.get('sentence', '')
                # Remove reference text from query if found_direct exists
                if found_direct:
                    # remove any combination of dossier and document numbers
                    numbers = found_direct.split('-')
                    sentence = sentence.replace(found_direct, '')
                    for number in numbers:
                        sentence = sentence.replace(number, '')
                query_parts.append(sentence)
            elif field == 'keywords':
                keywords = reference.get('reference_information', {}).get('keywords', [])
                query_parts.append(' '.join(keywords))
            elif field == 'summary':
                summary = reference.get('reference_information', {}).get('summary', '')
                if found_direct:
                    # remove any combination of dossier and document numbers
                    numbers = found_direct.split('-')
                    summary = summary.replace(found_direct, '')
                    for number in numbers:
                        summary = summary.replace(number, '')
                query_parts.append(summary)


        return ' '.join(filter(None, query_parts))

    def get_filters(self, minute_date, doc_type):
        """Get filter values based on system configuration."""
        filters = {}
        if self.filters.get('year', False):
            filters['year'] = minute_date[0:4]
        if self.filters.get('doc_type', False):
            filters['doc_type'] = doc_type
        return filters

FEATURE_COMBOS = [
    # Create all combinations of query fields and filters

    # Without filters
    FeatureBuilder(
        name='text',
        query_fields=['reference_text'],
        filters={}
    ),
    FeatureBuilder(
        name='text+sentence',
        query_fields=['reference_text', 'sentence'],
        filters={}
    ),
    FeatureBuilder(
        name='text+sentence+keywords',
        query_fields=['reference_text', 'sentence', 'keywords'],
        filters={}
    ),
    FeatureBuilder(
        name="text+sentence+summary",
        query_fields=['reference_text', 'sentence', 'summary'],
        filters={}
    ),
    FeatureBuilder(
        name='text+sentence+keywords+summary',
        query_fields=['reference_text', 'sentence', 'keywords', 'summary'],
        filters={}
    ),

    # With filters
    FeatureBuilder(
        name='text+sentence+keywords-year',
        query_fields=['reference_text', 'sentence', 'keywords'],
        filters={'year': True}
    ),
    FeatureBuilder(
        name='text+sentence+keywords-doctype',
        query_fields=['reference_text', 'sentence', 'keywords'],
        filters={'doc_type': True}
    ),
    FeatureBuilder(
        name='text+sentence+keywords-year+doctype',
        query_fields=['reference_text', 'sentence', 'keywords'],
        filters={'year': True, 'doc_type': True}
    ),
    FeatureBuilder(
        name='text+sentence+keywords+summary-year',
        query_fields=['reference_text', 'sentence', 'keywords', 'summary'],
        filters={'year': True}
    ),
    FeatureBuilder(
        name='text+sentence+keywords+summary-doctype',
        query_fields=['reference_text', 'sentence', 'keywords', 'summary'],
        filters={'doc_type': True}
    ),
    FeatureBuilder(
        name='text+sentence+keywords+summary-year+doctype',
        query_fields=['reference_text', 'sentence', 'keywords', 'summary'],
        filters={'year': True, 'doc_type': True}
    ),
]