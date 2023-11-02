import formula
import database_utils


database_utils.unify_suid_permissions()
value = formula.calculate_formula(0.01, 0.01)

print(value)