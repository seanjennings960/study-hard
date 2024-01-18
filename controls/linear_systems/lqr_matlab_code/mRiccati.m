function dXdt = mRiccati(t, X, A, B, L, R, Q)
X = reshape(X, size(A)); %Convert from "n^2"-by-1 to "n"-by-"n"
dXdt = -A.'*X - X*A - L + X*B*inv(R)*B.'*X; %Determine derivative
dXdt = dXdt(:); %Convert from "n"-by-"n" to "n^2"-by-1

end