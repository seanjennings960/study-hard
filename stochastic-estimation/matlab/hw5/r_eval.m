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