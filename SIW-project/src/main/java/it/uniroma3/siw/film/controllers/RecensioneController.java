package it.uniroma3.siw.film.controllers;

import javax.validation.Valid;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;

import it.uniroma3.siw.film.controllers.components.UserDetailsComponent;
import it.uniroma3.siw.film.model.Film;
import it.uniroma3.siw.film.model.Recensione;
import it.uniroma3.siw.film.model.Utente;
import it.uniroma3.siw.film.services.FilmService;
import it.uniroma3.siw.film.services.RecensioneService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Controller
@RequiredArgsConstructor
public class RecensioneController {

    private final RecensioneService recensioneService;
    private final UserDetailsComponent userDetailsComponent;
    private final FilmService filmService;

    @GetMapping("/recensioni/film/{id}")
    public String effettuaRecensione(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /recensione/film/" + id);
        Film film = this.filmService.getFilm(id);
        Recensione recensione = new Recensione();
        model.addAttribute("film", film);
        model.addAttribute("recensione", recensione);
        return "recensioneForm";
    }

    @PostMapping("/recensioni/film/{id}")
    public String salvaRecensione(@Valid @ModelAttribute Recensione recensione, BindingResult bindingResult, @PathVariable Long id, Model model){
        log.info("Richiesta POST /recensioni/film/" + id);
        Film film = this.filmService.getFilm(id);
        Utente utente = this.userDetailsComponent.getUtenteAutenticato();
        recensione.setFilm(film);
        recensione.setUtente(utente);

        if (!bindingResult.hasErrors()) {
            log.info("Parametri inseriti Corretti");
            this.recensioneService.salvaRecensione(recensione);
            return "redirect:/films/" + id;
        }

        log.warn("Parametri inseriti non Validi");
        model.addAttribute("film", film);
        return "recensioneForm";
    }

    @GetMapping("/recensioni/{id}/update")
    public String modificaRecensione(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /recensioni/" + id + "/update");
        Recensione recensione = this.recensioneService.getRecensione(id);
        Film film = recensione.getFilm();
        model.addAttribute("recensione", recensione);
        model.addAttribute("film", film);
        return "recensioneForm";
    }

    @GetMapping("/admin/recensioni/{id}/delete")
    public String cancellaRecensione(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /admin/recensione/" + id + "/delete");
        this.recensioneService.cancellaRecensione(id);
        return "forward:/admin/films";
    }
}
