pkg load instrument-control

% Open TCP connection to 127.0.0.1:2000
t0 = tcp("127.0.0.1", 2000);

% Parameters for the sine wave
amplitude = 10;
frequency = 1; % Hz
duration = 10; % seconds
dt = 0.1; % time step

t = 0:dt:duration; % time vector
sine_wave = amplitude * sin(2 * pi * frequency * t);

for i = 1:length(sine_wave)
    % Comando em formato JSON
    command = struct('force', sine_wave(i));
    tcp_write(t0, jsonencode(command));

    % Blocking read call, returns uint8 array
    data = tcp_read(t0, 1024, dt * 1000); % specify timeout in milliseconds
    % Convert uint8 array to string
    response = char(data');
    disp(response);

    % Pause for dt seconds
    pause(dt);
end

% Fechar a conexão
fclose(t0);
