clc
clear

A = [0 1; 0 0];
B = [0;1];
Q = [2 0; 0 2];
L = [1 0; 0 1];
R = 1;
K = zeros(4,1);
T = 1;
[t K] = ode45(@(t,K) mRiccati(t, K, A, B, L, R, Q), [T 0], Q);
K
Kend = K(end,:);
Kend = reshape(Kend, size(A))
