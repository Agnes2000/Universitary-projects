package it.uniroma3.siw.film.services;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import it.uniroma3.siw.film.model.Credenziali;
import it.uniroma3.siw.film.repository.CredenzialiRepository;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class CredenzialiService {

    private final PasswordEncoder passwordEncoder;
	private final CredenzialiRepository credentialsRepository;
	
	@Transactional
    public Credenziali salvaCredenziali(Credenziali credenziali) {
        credenziali.setPassword(this.passwordEncoder.encode(credenziali.getPassword()));
        return this.credentialsRepository.save(credenziali);
    }

	public Credenziali getCredenziali(Long id) {
		return this.credentialsRepository.findById(id).get();
	}

	public Credenziali getCredenziali(String username) {
		return this.credentialsRepository.findByUsername(username).get();
	}
    
    public boolean esistonoCredenziali(String username) {
        return this.credentialsRepository.existsByUsername(username);
    }

}
