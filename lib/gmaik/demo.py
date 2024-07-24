def sample(s):
    k = 1
    while k <= len(s)//2:
        strg = s[0:k]
        if len(s) % k != 0:
            k += 1
            continue
        strg = [strg] * (len(s) // k)
        strg = ''.join(strg)
        if s == strg:
            return k
        k += 1
    return -1

s = 'abcdabcdabcd'
ret = sample(s)
print(ret)
