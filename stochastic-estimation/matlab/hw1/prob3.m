function y_fit = ls_fit(x, y)
    M = size(x, 1);
    G = [ones(M, 1), x];
    m = (G' * G) \ (G' * y);
    y_fit = G * m;
end

function chi2 = goodness_of_fit(nu, y, y_fit, sigma)
    chi2 = sum((y - y_fit).^2 / sigma^2);
    p_chi2 = 1 - chi2cdf(chi2, nu);
    
    fprintf('Chi2 is: %g\n', chi2);
    fprintf('Probability of result given model: %g\n', p_chi2);
    fprintf('Degrees of freedom is %g so the std is: %g \n', nu, sqrt(2 * nu));
end

function run_fit(x, y, sigma, data_name)
    IMAGE_DIR = '../../tex/hw2/Images/';

    nu = size(x, 1) - 2;
    y_fit = ls_fit(x, y);
    chi2 = goodness_of_fit(nu, y, y_fit, sigma);

    % Data and fit line
    h = figure;
    plot(x, y, 'ro', x, y_fit, 'b');
    legend('data', 'fit');
    title(['Data and Fit Line for ' data_name])
    xlabel('x')
    ylabel('y')
    saveas(h, [IMAGE_DIR 'fit_' data_name '.jpg']);
    uiwait(h)

    % Residual Histogram
    h = figure;
    histogram(y - y_fit, 10);
    title(['Histogram of Residuals for ' data_name ...
           sprintf(' | goodness of fit = %g', chi2)])
    xlabel('error = y - y_fit')
    ylabel('Count')
    saveas(h, [IMAGE_DIR 'histogram_' data_name '.jpg']);
    uiwait(h)
end

load -ascii data1.dat
disp('Fitting data1.dat')
x = data1(:, 1); y = data1(:, 2);
sigma = 0.2;
run_fit(x, y, sigma, 'data1');

load -ascii data2.dat
disp('Fitting data1.dat')
x = data2(:, 1); y = data2(:, 2);
run_fit(x, y, sigma, 'data2');


