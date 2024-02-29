def replace_chars(input_str, k):
    result = list(input_str)
    window = set()

    for i, char in enumerate(input_str):
        if char in window:
            result[i] = '-'
        window.add(char)
        if i >= k:
            window.remove(result[i - k])

    return ''.join(result)

# 测试示例
input_str1 = "abcdefaxc"
input_str2 = "abcdefaxcqwertba"
k = 10
output_str1 = replace_chars(input_str1, k)
output_str2 = replace_chars(input_str2, k)
print("Output 1:", output_str1)
print("Output 2:", output_str2)
