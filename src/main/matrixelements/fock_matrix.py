from src.main.matrixelements import Matrix
from math import floor, ceil
import numpy as np


class FockMatrixRestricted(Matrix):

    def __init__(self, core_hamiltonian, repulsion_matrix):
        super().__init__()
        self.matrix_size = repulsion_matrix.shape[0]
        self.repulsion_matrix = repulsion_matrix
        self.core_hamiltonian = core_hamiltonian
        self.density_matrix_total = np.matrix([])

    def calculate_restricted(self, i, j):
        g_ij = 0
        for a in range(self.matrix_size):
            for b in range(self.matrix_size):
                coulomb_integral = self.repulsion_matrix.item(i, j, a, b)
                exchange_integral = self.repulsion_matrix.item(i, b, a, j)
                g_ij += self.density_matrix_total.item(a, b) * (coulomb_integral - 1/2 * exchange_integral)
        return g_ij

    def create(self, density_matrix):
        self.density_matrix_total = density_matrix
        fock_matrix = self.core_hamiltonian + self.create_matrix(self.calculate_restricted)
        return fock_matrix


class FockMatrixUnrestricted(Matrix):

    def __init__(self, core_hamiltonian, repulsion_matrix):
        super().__init__()
        self.matrix_size = repulsion_matrix.shape[0]
        self.repulsion_matrix = repulsion_matrix
        self.core_hamiltonian = core_hamiltonian
        self.density_matrix_alph = np.matrix([])
        self.density_matrix_beta = np.matrix([])
        self.density_matrix_total = np.matrix([])

    def calc_unrestricted_alph(self, i, j):
        g_ij = 0
        for a in range(self.matrix_size):
            for b in range(self.matrix_size):
                coulomb = self.density_matrix_total.item(a, b) * self.repulsion_matrix.item(i, j, a, b)
                exchange = self.density_matrix_alph.item(a, b) * self.repulsion_matrix.item(i, b, a, j)
                g_ij += coulomb - exchange
        return g_ij

    def calc_unrestricted_beta(self, i, j):
        g_ij = 0
        for a in range(self.matrix_size):
            for b in range(self.matrix_size):
                coulomb = self.density_matrix_total.item(a, b) * self.repulsion_matrix.item(i, j, a, b)
                exchange = self.density_matrix_beta.item(a, b) * self.repulsion_matrix.item(i, b, a, j)
                g_ij += coulomb - exchange
        return g_ij

    def create(self, density_matrix_alph, density_matrix_beta):
        self.density_matrix_alph = density_matrix_alph
        self.density_matrix_beta = density_matrix_beta
        self.density_matrix_total = density_matrix_alph + density_matrix_beta
        fock_matrix_alph = self.core_hamiltonian + self.create_matrix(self.calc_unrestricted_alph)
        fock_matrix_beta = self.core_hamiltonian + self.create_matrix(self.calc_unrestricted_beta)
        return fock_matrix_alph, fock_matrix_beta


class FockMatrixConstrained(FockMatrixUnrestricted):

    def __init__(self, core_hamiltonian, repulsion_matrix, electrons, multiplicity, linear_algebra):
        super().__init__(core_hamiltonian, repulsion_matrix)
        self.linear_algebra = linear_algebra
        self.electrons_alph = ceil(electrons / 2) + floor(multiplicity / 2)
        self.electrons_beta = floor(electrons / 2) - floor(multiplicity / 2)
        self.orthonormal_fock_alph = np.matrix([])
        self.orthonormal_fock_beta = np.matrix([])
        self.orthonormal_fock_closed = np.matrix([])

    def create(self, density_matrix_alph, density_matrix_beta):
        self.density_matrix_alph = density_matrix_alph
        self.density_matrix_beta = density_matrix_beta
        self.density_matrix_total = density_matrix_alph + density_matrix_beta

        fock_matrix_alph = self.core_hamiltonian + self.create_matrix(self.calc_unrestricted_alph)
        fock_matrix_beta = self.core_hamiltonian + self.create_matrix(self.calc_unrestricted_beta)

        self.orthonormal_fock_alph = self.linear_algebra.orthonormalize(fock_matrix_alph)
        self.orthonormal_fock_beta = self.linear_algebra.orthonormalize(fock_matrix_beta)
        self.orthonormal_fock_closed = (self.orthonormal_fock_alph + self.orthonormal_fock_beta) / 2

        orthonormal_constrained_alph = self.create_matrix(self.calc_constrained_alph)
        orthonormal_constrained_beta = self.create_matrix(self.calc_constrained_beta)

        constrained_fock_matrix_alph = self.linear_algebra.non_orthonormal(orthonormal_constrained_alph)
        constrained_fock_matrix_beta = self.linear_algebra.non_orthonormal(orthonormal_constrained_beta)

        return constrained_fock_matrix_alph, constrained_fock_matrix_beta

    def calc_constrained_alph(self, i, j):

        # (i is virtual and j is open or closed) or (j is virtual and i is open or closed)
        if i > (self.electrons_alph and self.electrons_beta) and j < (self.electrons_alph or self.electrons_beta) \
        or j > (self.electrons_alph and self.electrons_beta) and i < (self.electrons_alph or self.electrons_beta):

            return self.orthonormal_fock_closed.item(i, j)

        else:

            return self.orthonormal_fock_alph.item(i, j)

    def calc_constrained_beta(self, i, j):

        # (i is virtual and j is open or closed) or (j is virtual and i is open or closed)
        if i > (self.electrons_alph and self.electrons_beta) and j < (self.electrons_alph or self.electrons_beta) \
        or j > (self.electrons_alph and self.electrons_beta) and i < (self.electrons_alph or self.electrons_beta):

            return self.orthonormal_fock_closed.item(i, j)

        else:

            return self.orthonormal_fock_beta.item(i, j)