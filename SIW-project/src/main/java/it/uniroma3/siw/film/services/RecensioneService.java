package it.uniroma3.siw.film.services;

import java.util.List;

import javax.transaction.Transactional;

import org.springframework.stereotype.Service;

import it.uniroma3.siw.film.model.Film;
import it.uniroma3.siw.film.model.Recensione;
import it.uniroma3.siw.film.model.Utente;
import it.uniroma3.siw.film.repository.RecensioneRepository;
import lombok.RequiredArgsConstructor;


@Service
@RequiredArgsConstructor
public class RecensioneService {

    private final RecensioneRepository recensioneRepository;

    @Transactional
    public void salvaRecensione(Recensione recensione) {
        this.recensioneRepository.save(recensione);
    }

    @Transactional
    public void cancellaRecensione(Long id) {
        this.recensioneRepository.deleteById(id);
    }

    public List<Recensione> getRecensioni(Utente utente) {
        return this.recensioneRepository.findByUtente(utente);
    }

    public Recensione getRecensione(Long id) {
        return this.recensioneRepository.findById(id).get();
    }

    public boolean esisteRecensione(Utente utente, Film film) {
        return this.recensioneRepository.existsByUtenteAndFilm(utente, film);
    }
    
}
