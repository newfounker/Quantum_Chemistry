from src.main.objects import PrimitiveBasisFactory
import numpy as np
from src.main.integrals import OverlapIntegral

class KineticEnergyIntegral:

    def __init__(self, basis_set_array):
        self.basis_set_array = basis_set_array

    def calculate(self, i, j):
        t_ij = 0
        primitive_gaussian_array_i = self.basis_set_array[i].primitive_gaussian_array
        primitive_gaussian_array_j = self.basis_set_array[j].primitive_gaussian_array
        for a in range(0, len(primitive_gaussian_array_i)):
            for b in range(0, len(primitive_gaussian_array_j)):
                a_1 = primitive_gaussian_array_i[a].exponent
                a_2 = primitive_gaussian_array_j[b].exponent
                c_1 = primitive_gaussian_array_i[a].contraction
                c_2 = primitive_gaussian_array_j[b].contraction
                l_1 = primitive_gaussian_array_i[a].integral_exponents
                l_2 = primitive_gaussian_array_j[b].integral_exponents
                n_1 = (((2 * a_1) / np.pi)**(3/4)) * (((((8 * a_1)**(l_1[0] + l_1[1] + l_1[2])) * np.math.factorial(l_1[0]) * np.math.factorial(l_1[1]) * np.math.factorial(l_1[2])) / (np.math.factorial(2 * l_1[0]) * np.math.factorial(2 * l_1[1]) * np.math.factorial(2 * l_1[2])))**(1/2))
                n_2 = (((2 * a_2) / np.pi)**(3/4)) * (((((8 * a_2)**(l_2[0] + l_2[1] + l_2[2])) * np.math.factorial(l_2[0]) * np.math.factorial(l_2[1]) * np.math.factorial(l_2[2])) / (np.math.factorial(2 * l_2[0]) * np.math.factorial(2 * l_2[1]) * np.math.factorial(2 * l_2[2])))**(1/2))
                primitive_gaussian_array_k = PrimitiveBasisFactory().del_operator(primitive_gaussian_array_j[b])
                s_ij = 0
                for c in range(0, len(primitive_gaussian_array_k)):
                    c_3 = primitive_gaussian_array_k[c].contraction
                    s_ij += n_1 * n_2 * c_1 * c_2 * c_3 * OverlapIntegral().primitive_overlap_integral(primitive_gaussian_array_i[a], primitive_gaussian_array_k[c])
                t_ij += s_ij
        return t_ij
