def distinct(subsequence):

    return int(''.join(sorted(list(set([i for i in str(subsequence)])))))

print(distinct(122333444455555))