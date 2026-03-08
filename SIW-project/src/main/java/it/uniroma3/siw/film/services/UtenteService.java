package it.uniroma3.siw.film.services;

import javax.transaction.Transactional;

import org.springframework.stereotype.Service;

import it.uniroma3.siw.film.model.Utente;
import it.uniroma3.siw.film.repository.UtenteRepository;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class UtenteService {

    private final UtenteRepository utenteRepository;

    @Transactional
    public void salvaUtente(Utente utente) {
        this.utenteRepository.save(utente);
    }
    
}
