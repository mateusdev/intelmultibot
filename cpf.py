def formata_cpf(cpf):
    cpf_formated = ''.join([i for i in cpf if i.isdigit()])
    cpf_formated = int(cpf_formated)
    return cpf_formated

def checa_regiao_fiscal(cpf):
    if type(cpf) is str:
        return None

    remainder1 = cpf % 1000
    remainder2 = remainder1 % 100
    digit = (remainder1 - remainder2) / 100

    states = []

    if digit == 0:
        digit = 10
        states = ['RS']
    elif digit == 1:
        states = ['DF', 'GO', 'MT', 'MS', 'TO']
    elif digit == 2:
        states = ['AC', 'AP', 'AM', 'PA', 'RO', 'RR']
    elif digit == 3:
        states = ['CE', 'MA', 'PI']
    elif digit == 4:
        states = ['AL', 'PB', 'PE', 'RN']
    elif digit == 5:
        states = ['BA', 'SE']
    elif digit == 6:
        states = ['MG']
    elif digit == 7:
        states = ['ES', 'RJ']
    elif digit == 8:
        states = ['SP']
    elif digit == 9:
        states = ['PR', 'SC']
    else:
        return None

    return digit, states


def checa_cpf(cpf_sent):
    cpf = formata_cpf(cpf_sent)
    if cpf is None:
        return None

    region = checa_regiao_fiscal(cpf)
    if region is None:
        return None

    # Boring mathematical stuff
    digits = cpf % 100
    cpf = cpf // 100
    v1, v2 = 0, 0

    generator = [int(x) for x in str(cpf)[::-1]]
    i = 0
    for num in generator:
        v1 = v1 + num * (9 - (i % 10))
        v2 = v2 + num * (9 - ((i + 1) % 10))
        i += 1

    v1 = (v1 % 11) % 10
    v2 = v2 + v1 * 9
    v2 = (v2 % 11) % 10

    # Checar veracidade
    if v1 == 10:
        v1 = 0
    if v2 == 10:
        v2 = 0

    v1 = v1 * 10 + v2
    if v1 == digits:
        return [cpf_sent, region]

    return None