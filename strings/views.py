import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from .models import AnalyzedString
from .utils import analyze_string


@csrf_exempt
@require_http_methods(["POST"])
def create_string(request):
    try:
        # Try to parse JSON
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    value = data.get("value", None)

    # Handle missing 'value' field
    if value is None:
        return JsonResponse({"error": 'Missing "value" field'}, status=400)

    # Handle wrong type
    if not isinstance(value, str):
        return JsonResponse({"error": '"value" must be a string'}, status=422)

    # Handle empty string
    if not value.strip():
        return JsonResponse({"error": '"value" cannot be empty'}, status=400)

    # Analyze string and generate hash
    hash_id, props = analyze_string(value)

    # Handle duplicate
    if AnalyzedString.objects.filter(id=hash_id).exists():
        return JsonResponse({"error": "String already exists"}, status=409)

    # Save new object
    obj = AnalyzedString.objects.create(
        id=hash_id,
        value=value,
        length=props["length"],
        is_palindrome=props["is_palindrome"],
        unique_characters=props["unique_characters"],
        word_count=props["word_count"],
        sha256_hash=props["sha256_hash"],
        character_frequency_map=props["character_frequency_map"]
    )

    return JsonResponse({
        "id": obj.id,
        "value": obj.value,
        "properties": props,
        "created_at": obj.created_at.isoformat()
    }, status=201)


@require_http_methods(["GET"])
def get_string(request, string_value):
    hash_id, _ = analyze_string(string_value)
    try:
        obj = AnalyzedString.objects.get(id=hash_id)
        return JsonResponse({
            "id": obj.id,
            "value": obj.value,
            "properties": {
                "length": obj.length,
                "is_palindrome": obj.is_palindrome,
                "unique_characters": obj.unique_characters,
                "word_count": obj.word_count,
                "sha256_hash": obj.sha256_hash,
                "character_frequency_map": obj.character_frequency_map
            },
            "created_at": obj.created_at.isoformat()
        }, status=200)
    except AnalyzedString.DoesNotExist:
        return JsonResponse({"error": "String not found"}, status=404)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_string(request, string_value):
    hash_id, _ = analyze_string(string_value)
    try:
        obj = AnalyzedString.objects.get(id=hash_id)
        obj.delete()
        return JsonResponse({}, status=204)
    except AnalyzedString.DoesNotExist:
        return JsonResponse({"error": "String not found"}, status=404)


@require_GET
def list_strings(request):
    qs = AnalyzedString.objects.all()
    filters_applied = {}

    min_length = request.GET.get("min_length")
    if min_length and min_length.isdigit():
        qs = qs.filter(length__gte=int(min_length))
        filters_applied["min_length"] = int(min_length)

    max_length = request.GET.get("max_length")
    if max_length and max_length.isdigit():
        qs = qs.filter(length__lte=int(max_length))
        filters_applied["max_length"] = int(max_length)

    is_palindrome = request.GET.get("is_palindrome")
    if is_palindrome in ["true", "false"]:
        val = is_palindrome.lower() == "true"
        qs = qs.filter(is_palindrome=val)
        filters_applied["is_palindrome"] = val

    contains_char = request.GET.get("contains_character")
    if contains_char:
        qs = qs.filter(value__icontains=contains_char)
        filters_applied["contains_character"] = contains_char

    word_count = request.GET.get("word_count")
    if word_count and word_count.isdigit():
        qs = qs.filter(word_count=int(word_count))
        filters_applied["word_count"] = int(word_count)

    data = [{
        "id": obj.id,
        "value": obj.value,
        "properties": {
            "length": obj.length,
            "is_palindrome": obj.is_palindrome,
            "unique_characters": obj.unique_characters,
            "word_count": obj.word_count,
            "sha256_hash": obj.sha256_hash,
            "character_frequency_map": obj.character_frequency_map
        },
        "created_at": obj.created_at.isoformat()
    } for obj in qs]

    return JsonResponse({
        "data": data,
        "count": len(data),
        "filters_applied": filters_applied
    }, status=200)


@require_GET
def filter_by_natural_language(request):
    query = request.GET.get("query", "").lower()
    qs = AnalyzedString.objects.all()

    if "palindrome" in query:
        qs = qs.filter(is_palindrome=True)

    if "longer than" in query and "characters" in query:
        try:
            num = int(query.split("longer than")[1].split("characters")[0].strip())
            qs = qs.filter(length__gt=num)
        except ValueError:
            pass

    if "one word" in query or "single word" in query:
        qs = qs.filter(word_count=1)

    if "unique characters" in query:
        qs = qs.filter(unique_characters__gte=2)

    data = [{
        "id": obj.id,
        "value": obj.value,
        "properties": {
            "length": obj.length,
            "is_palindrome": obj.is_palindrome,
            "unique_characters": obj.unique_characters,
            "word_count": obj.word_count,
            "sha256_hash": obj.sha256_hash,
            "character_frequency_map": obj.character_frequency_map
        },
        "created_at": obj.created_at.isoformat()
    } for obj in qs]

    return JsonResponse({
        "data": data,
        "count": len(data),
        "query": query
    }, status=200)
