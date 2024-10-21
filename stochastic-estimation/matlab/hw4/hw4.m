load hw4.mat d

function w = uniform_window(m)
    w = ones(m, 1);
end

function w = hann_window(n)
    w = 0.5 * (1 - cos(2 * pi * (0:n-1)' / (n-1)));
end

function w = blackman_window(n)
    % Use 0:m-1 so that the window has size m and is symmetric starting
    % and ending at 0.
    x = (0:n-1)' / (n-1);
    w = 0.42 - 0.5 * cos(2 * pi * x) + 0.08 * cos(4 * pi * x);
end

function S = periodogram(x, N, overlap, window_func)
    L = size(x, 1);  % Total number of samples
    M = floor((L-overlap) / (N - overlap));

    w = window_func(N);
    S = zeros(N,1);
    index = 1:N;
    for i=1:M
        S = S + abs(fft(x(index) .* w)).^2;
        index = index + (N - overlap);
    end
    S = fftshift(S) / (M * N^2);
    % S = mag2db(S);
end


x = d(:, 1); y = d(:, 2);

N = 4096;
overlap = N / 4;
t = d(:, 1); x = d(:, 2);
figure()
plot(t, x)
title("Signal")
xlabel("Time (t)")
ylabel("x(t)")
S_uniform = periodogram(x, N, overlap, @uniform_window);
S_hann = periodogram(x, N, overlap, @hann_window);
S_blackman = periodogram(x, N, overlap, @blackman_window);

delta_t = t(2) - t(1);
delta_f = 1 / (N * delta_t);
f = delta_f * ((0:N-1) - N/2);

disp("Power from spectral estimates:")
fprintf("Uniform: %g\n", sum(S_uniform))
fprintf("Hann: %g\n", sum(S_hann))
fprintf("blackman: %g\n", sum(S_blackman))

figure()
plot(f, mag2db(S_uniform), f, mag2db(S_hann), f, mag2db(S_blackman))
legend("uniform", "Hann", "Blackman")
xlabel("Frequency (Hz)")
ylabel("Spectral Estimate (dB)")

figure()
hold on;
for N=[256, 4096, 64000]
    overlap = N / 4;  % 25% overlap
    S = periodogram(x, N, overlap, @blackman_window);
    delta_f = 1 / (N * delta_t);
    fprintf("Energy in spectral estimate (N=%g): %g\n", N, sum(S))
    f = delta_f * ((0:N-1) - N/2);
    plot(f, mag2db(S))
end
title("Peroidogram Spectral Estimate vs window length")
legend("N=256", "N=4096", "N=64,000")
xlabel("Frequency (Hz)")
ylabel("Power density")

function Rx = autocorrelation(x)
    L = size(x, 1);
    Rx = zeros(size(x));
    for n=1:L
        Rx(n) = x(1:L-n+1)' * x(n:L) / (L-n);
    end
end

function Sx = spectrumFromRx(Rx, N)
    Sx = abs(fft(blackman_window(2*N) .* [0; Rx(N:-1:2); Rx(1:N-1); 0 ]));
    % Normalize
    Sx = Rx(1) * Sx / sum(Sx);
    % Sx = mag2db(Sx);
end

figure()
Rx = autocorrelation(x);
plot(t, Rx)
title("Autocorrelation function")
xlabel("Lag (tau)")
ylabel("R(tau)")

power_Rx = Rx(1);
fprintf("Power from autocorrelation: %g\n", power_Rx)

figure()
hold on;
delta_t = t(2) - t(1);

for N=[256, 2048, 128000/2]
    delta_f = 1 / (2 * N * delta_t);
    f = delta_f * ((0:2*N - 1) - N);
    Sx = spectrumFromRx(Rx, N);
    plot(f, fftshift(mag2db(Sx)))
    power_Sx = sum(Sx);
    fprintf("Power from spectral estimate (N=%g): %g\n", N, power_Sx)
end
title("Spectrum From BT Method")
xlabel("Frequency (Hz)")
ylabel("Power Density (dB)")
legend("N=256", "N=2048", "N=128,000")