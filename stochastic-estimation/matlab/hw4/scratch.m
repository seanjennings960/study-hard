N = 200;  % Number of samples
f = 10;  % Frequency
% T = 3 % Total Time
delta_t = 0.025;


t = (0:delta_t:(N-1)*delta_t)';
x = cos(2 * pi * f * t + 0.1);
plot(t, x)
figure()

Xf = fft(x) / N;
Xf = Xf(1:N/2);
[x_max, maxI] = max(Xf);
delta_t = t(2) - t(1);
delta_f = 1 / (N*delta_t);
f_list = delta_f * ((0:N/2-1)');
% plot(f_list, abs(Xf));

S = mag2db(abs(Xf).^2);

T = max(t);
f_sinc = linspace(0, 21, 1001);
S_analytic = T / 2 * (sinc(T*(f_sinc - f)) - sinc(T * (f_sinc + f)));
semilogx(f_list, S, "o", f_sinc, mag2db(S_analytic.^2));


% hold on;
% for phase=0:0.5:7
%     x = sin(2 * pi * f * t + phase);
%     S = abs(fft(x)).^2;
%     S = mag2db(fftshift(S));
%     delta_t = t(2) - t(1);
%     delta_f = 1 / (N*delta_t);
%     f_plot = delta_f * ((0:N-1)' - N/2);
%     % plot(t, x)
%     plot(f_plot(N/2:end), S(N/2:end))
% end
% f_plot = f_plot(N/2:end)
% plot(f_plot, mag2db(sinc(f_plot - f).^2))