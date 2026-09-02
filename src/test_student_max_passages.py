from random import choices
from statistics import mean

PROBA_COEFF = 0.2  # Coefficient de probabilité pour les passages ultérieurs

def simulate_once(n: int) -> int:
    """Nombre de passages nécessaires pour que tous les élèves soient
    passés au moins une fois."""

    passages = [0] * n
    weights = [1.0] * n

    remaining = n
    total = 0
    students = list(range(n))

    while remaining:
        student = choices(students, weights=weights, k=1)[0]

        if passages[student] == 0:
            remaining -= 1

        passages[student] += 1
        weights[student] *= PROBA_COEFF

        total += 1

    return total


def monte_carlo(n: int, nb_iter: int = 10**4) -> float:
    return mean(simulate_once(n) for _ in range(nb_iter))


if __name__ == "__main__":
    for n in (20, 25, 30):
        avg = monte_carlo(n)
        print(f"{n:2d} élèves : {avg:.2f} passages")