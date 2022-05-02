from context.passFinderContext import extract_context_passfinder_all, merge_passfinder_context

if __name__ == '__main__':
    language = 'csharp'
    base = '/media/rain/data/csharp_zip'
    extract_context_passfinder_all(
        base,
        language,
        "pass"
    )
    extract_context_passfinder_all(
        base,
        language,
        "string"
    )

