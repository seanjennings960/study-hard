N = 1e5;
n = randn(N, 1);

function S = periodogram(x, N, overlap, window_func)
    L = size(x, 1);  % Total number of samples
    P = floor((L-overlap) / (N - overlap));

    w = window_func(N);
    wss = sum(w.^2)/N;
    S = zeros(N,1);
    index = 1:N;
    for i=1:P
        S = S + abs(fft(x(index) .* w)).^2;
        index = index + (N - overlap);
    end
    S = fftshift(S) / (M * N^2 * wss);
end

function Rx = autocorrelation(x)
    L = size(x, 1);
    Rx = zeros(size(x));
    disp(L)
    for n=1:L
        Rx(n) = k(1:L-n+1)' * x(n:L) / (L-n);
    end
end

N_sample = 4096;
overlap = N_sample/4;
S_f = periodogram(n, N_sample, overlap, @blackman);


figure()
plot(n)
xlabel("Index (n)")
ylabel("x(n)")
title("White Gaussian Noise (\sigma=1)")

f_fft = (0:N-1) - N/2;
S_f_fft = fftshift(abs(fft(n).^2)/N^2);

f_periodogram = (0:N_sample-1) - N_sample/2;
N_sample = 4096;
overlap = N_sample/4;
S_f_periodogram = periodogram(n, N_sample, overlap, @blackman);

figure()
plot(f_periodogram, S_f_periodogram)
ylim([0, 5e-4])
xlabel("Frequency bin (k)")
ylabel("S_x(k)")
title("Power Spectral Density of white noise")

fprintf("Power from original: %g\n", 1/N * n' * n);
fprintf("Power from spectrum: %g\n", sum(S_f_fft));
fprintf("Power from periodogram: %g\n", sum(S_f_periodogram));

figure()
Rx = autocorrelation(n);
plot(Rx);
title("Autocorrelation of Gaussian White Noise")
xlabel("Lag index (k)")
ylabel("E[x_n x_{n+k}]")

%% Autocorrelation of Cosine

t = (0:0.0001:1)';
f = 4;
x = cos(2 * pi * f * t + pi/4);
Rx = autocorrelation(x);
figure()
plot(t, Rx)
title("Autocorrelation for x(t) = cos(2\pi f t + \phi) | f = 2Hz, \phi=\pi/4")
xlabel("\tau = Lag (seconds)")
ylabel("R_x(\tau)")

%% Transfer function Identification

function T = polyMat(s, M)
    T = zeros(size(s, 1), M);
    for m = 1:M
        T(:, m) = s.^m;
    end
end

function [m, h_hat, cond_num] = rational_fit(omega, h, L, K)
    N = size(omega, 1);
    s = complex(0, omega);
    S = [ones(N, 1), polyMat(s, L)];
    T = polyMat(s, K);
    G = [S, -diag(h) * T];
    
    % Split real and imaginary parts so that model is real.
    G_bar = [real(G); imag(G)]; h_bar = [real(h); imag(h)];
    m = inv(G_bar' * G_bar) * G_bar' * h_bar;
    disp("")
    h_hat = (S * m(1:L+1))./(1 + T * m(L+2:end));
    cond_num = cond(G_bar);
end

function total = r_eval(r_solution, omega)
    p = r_solution.Poles;
    c = r_solution.Residues;
    n = r_solution.NumPoles;
    
    s = 1j * omega;
    total = zeros(size(omega));
    for i=1:n
        total = total + c(:, :, i) ./ (s - p(i, :));
    end
end

load hw5/hw5_2.mat d

omega = d(:, 1);
freq = omega / (2 * pi);
h = complex(d(:, 2), d(:, 3));

% sigmas = [0];  % No Noise
min_exp = -9;
max_exp = -1;
sigmas = logspace(min_exp, max_exp, max_exp - min_exp + 1);
N = size(h, 1);
P = length(sigmas);

h_rand = zeros(N, P);
% Least squares model parameters m = [a_0, a_1, ..., a_L, b_1, ..., b_K]
L = 2; K = 2;
% L = 1; K = 1;

m_least_squares = zeros(L + K + 1, P);
% LS model:
h_hat_least_squares = complex(zeros(N, P), zeros(N, P));
% Rational model:
m_rational = createArray(P, "rational");
h_hat_rational = complex(zeros(N, P), zeros(N,P));
cond_numbers = zeros(P, 1);

for k=1:length(sigmas)
    sigma = sigmas(k);
    h_rand(:, k) = h + sigma * (randn(size(h)) + 1i * randn(size(h))) / sqrt(2);

    % Fit LS rational model
    [m, h_hat, cond_num] = rational_fit(omega, h_rand(:, k), L, K);
    m_least_squares(:, k) = m;
    h_hat_least_squares(:, k) = h_hat;
    cond_numbers(k) = cond_num;

    % Fit Matlab rational model
    m_rational(k) = rational(freq, h_rand(:, k), "MaxPoles", 2);
    h_hat_rational(:, k) = r_eval(m_rational(k), omega);
end


%% Compute the poles and zeros
function fprintc(f_string, v_complex)
    for v = v_complex
        fprintf(f_string, real(v), imag(v));
    end
end

zs_ls = zeros(P, L);
ps_ls = zeros(P, K);
for p=1:P
    % Compute the poles and zeros
    zs_ls(p, :) = roots(m_least_squares(L+1:-1:1, p));
    ps_ls(p, :) = roots([m_least_squares(end:-1:L+2, p); 1]);
end


disp("Poles and Zeros from From Least squares")
for p=1:P
    fprintf("Sigma=%g\n", sigmas(p))
    fprintc("Zeros: %g + j %g\n", zs_ls(p, :))
    fprintc("Poles: %g + j %g\n", ps_ls(p, :))
end

ps_rational = zeros(P, K);
for p=1:P
    ps_rational(p, :) = m_rational.Poles;
end
disp("Poles MATLAB rational")
for p=1:P
    fprintf("Sigma=%g\n", sigmas(p))
    fprintc("Poles: %g + j %g\n", ps_rational(p, :))
end

%% Bode plots

function plot_bode(sigmas, omega, h_rand, h_hat)
    % Plot magnitude
    figure()
    labels = [];
    colors = get(gca, "ColorOrder");
    for k = 1:length(sigmas)
        sigma = sigmas(k);
4
        color = colors(rem(k, size(colors, 1)) + 1, :);
        loglog(omega, abs(h_rand(:, k)), "o", "Color", color)
        hold on
        loglog(omega, abs(h_hat(:, k)), "-", "Color", color)
        labels = [labels,
                  sprintf("Data (sigma=%g)", sigma),
                  sprintf("Fit (sigma=%g)", sigma)];
    end
    legend(labels)
    xlabel("\omega")
    ylabel("|H(\omega)|")
end

plot_bode(sigmas, omega, h_rand, h_hat_least_squares)
%% Plot for rational fit solution
plot_bode(sigmas, omega, h_rand, h_hat_rational)
title("Estimated frequency response for rational fit function")

%% Condition Numbers
max_poles = 10;
cond_num_versus_poles = zeros(max_poles, 1);
for k=1:max_poles
    [~, ~, cond_num] = rational_fit(omega, h, L, k);
    cond_num_versus_poles(k) = cond_num;
end
figure()
loglog(sigmas, cond_numbers)
title("Condition number of G versus input noise \sigma")
xlabel("\sigma")
ylabel("\kappa(G)")
ylim([1e5, 1e10])
figure()
semilogy(1:max_poles, cond_num_versus_poles)
title("Condition number of G as a function of K")
xlabel("K (number of poles)")
ylabel("\kappa(G)")



%% Error Plots

function plotError(err, sigma, normalize)
    if normalize
        err = err / sigma;
    end
    figure()
    histogram(err, "Normalization","pdf");
    hold on;
    x = linspace(min(err), max(err));
    if normalize
        plot(x, 2 * normpdf(x))
    else
        plot(x, 2 * normpdf(x, 0, sigma));
    end
    xlabel("Error ($$|\hat{H}_m(s) - h|$$)", "Interpreter","latex")
    ylabel("PDF")
    legend("PDF of Error", sprintf("Normal PDF for sigma=%g", sigma))
end

error_ls = abs(h_hat_least_squares - h_rand);
error_rational = abs(h_hat_rational - h_rand);
k_sigma = 1;
sigma = sigmas(k_sigma);
plotError(error_ls(:, k_sigma), sigma, false)
title(sprintf("Rational fit error distribution (sigma=%g)", sigma))
set(gca, "YScale", "log")

plotError(error_rational(:, k_sigma), sigma, false)
title(sprintf("Rational fit error distribution (sigma=%g)", sigma))


%% Chi2 plots

chi2_ls = sum(abs(h_hat_least_squares - h_rand).^2, 1) ./ sigmas.^2;
chi2_rational = sum(abs(h_hat_rational - h_rand).^2, 1) ./ sigmas.^2;
nu = N - 4;
chi2_std = sqrt(2 * nu);

figure()
loglog(sigmas, chi2_ls);
hold on
loglog(sigmas, chi2_rational);
yline([nu + chi2_std, nu - chi2_std])
legend("Least squares fit", "MATLAB rational fit", "E[\chi^2] +/- 1 std")
xlabel("Sigma")
ylabel("\chi^2")
title("\chi^2 coefficient versus \sigma")


%% Pearson Correlation Coefficient
function rho = pearson_coefficient(h, h_fit)
    % h and h_fit are (NxM) matrices, so perform summations
    % over 1st dim to return a vector of length P for each
    % value of sigma.
    % The denominator of the pearson coefficient is equivalent to the
    % vector 2-norm in C^N (N-dimension vectors over the field of complex
    % numbers).
    rho = abs(sum(h .* conj(h_fit), 1)) ./ ...
        (vecnorm(h, 2, 1) .* vecnorm(h_fit, 2, 1));
end
pearson_ls = pearson_coefficient(h_rand, h_hat_least_squares);
pearson_rational = pearson_coefficient(h_rand, h_hat_rational);

figure()
loglog(sigmas, pearson_ls)
hold on
semilogx(sigmas, pearson_rational)
legend("Least Squares", "rational fit")
ylim([0, 1.5])
title("Pearson Correlation Coefficient as a function of noise")
ylabel("\rho")
xlabel("\sigma")