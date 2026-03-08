package it.uniroma3.siw.film.controllers;

import java.io.IOException;

import javax.validation.Valid;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.StringUtils;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import it.uniroma3.siw.film.controllers.components.UserDetailsComponent;
import it.uniroma3.siw.film.controllers.components.validators.FilmValidator;
import it.uniroma3.siw.film.model.Attore;
import it.uniroma3.siw.film.model.Film;
import it.uniroma3.siw.film.model.Utente;
import it.uniroma3.siw.film.services.AttoreService;
import it.uniroma3.siw.film.services.FilmService;
import it.uniroma3.siw.film.services.RecensioneService;
import it.uniroma3.siw.film.services.RegistaService;
import it.uniroma3.siw.film.utils.FileUploadUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Controller
@RequiredArgsConstructor
public class FilmController {

    private final FilmService filmService;
    private final RegistaService registaService;
    private final AttoreService attoreService;
    private final FilmValidator filmValidator;
    private final RecensioneService recensioneService;
    private final UserDetailsComponent userDetailsComponent;

    @GetMapping("/admin/films")
    public String getFilms(Model model) {
        log.info("Richiesta GET /admin/films");
        model.addAttribute("films", this.filmService.getFilms());
        return "admin/films";
    }

    @GetMapping("/admin/films/create")
    public String newFilm(Model model) {
        log.info("Richiesta GET /admin/films/create");
        model.addAttribute("film", new Film());
        model.addAttribute("registi", this.registaService.getRegisti());
        return "admin/filmForm";
    }

    @GetMapping("/admin/films/{id}/update")
    public String modificaFilm(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /admin/films/" + id + "/update");
        model.addAttribute("film", this.filmService.getFilm(id));
        model.addAttribute("registi", this.registaService.getRegisti());
        return "admin/filmForm";
    }

    @GetMapping("/admin/films/{id}/delete")
    public String cancellaFilm(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /admin/films/" + id + "/delete");
        this.filmService.cancellaFilm(id);
        model.addAttribute("films", this.filmService.getFilms());
        return "admin/films";
    }

    @GetMapping("/admin/films/{filmId}/attori")
    public String aggiungiAttoreAfilm(@PathVariable Long filmId, Model model) {
        log.info("Richiesta GET /admin/films/" + filmId + "/attori");
        model.addAttribute("film", this.filmService.getFilm(filmId));
        model.addAttribute("attori", this.attoreService.getAttori());
        return "admin/aggiungiAttore";
    }

    @GetMapping("/admin/films/{filmId}/attori/{attoreId}/remove")
    private String rimuoviAttoreDalFilm(@PathVariable Long filmId, @PathVariable Long attoreId, Model model) {
        log.info("/admin/films/" + filmId + "/attori/" + attoreId + "/remove");
        Film film = this.filmService.getFilm(filmId);
        Attore attore = this.attoreService.getAttore(attoreId);
        film.getAttori().remove(attore);
        film = this.filmService.salvaFilm(film);
        model.addAttribute("film", film);
        return "film";
    }

    @GetMapping("/admin/films/{filmId}/aggiungiAttore/{attoreId}")
    public String aggiungiAttore(@PathVariable Long filmId, @PathVariable Long attoreId,Model model) {
        log.info("Richiesta GET /admin/films/" + filmId + "/aggiungiAttore/" + attoreId);
        Film film = this.filmService.getFilm(filmId);
        Attore attore = this.attoreService.getAttore(attoreId);
        film.getAttori().add(attore);
        film = this.filmService.salvaFilm(film);
        model.addAttribute("film", film);
        return "film";
    }

    @PostMapping("/admin/films/create")
    public String saveFilm(@Valid @ModelAttribute Film film, @RequestParam("image") MultipartFile multipartFile, BindingResult bindingResult, Model model) throws IOException {
        log.info("Richiesta POST /admin/films/new");
        this.filmValidator.validate(film, bindingResult);

        if (!bindingResult.hasErrors()) {
            log.info("Parametri inseriti Corretti");
            String fileName = StringUtils.cleanPath(multipartFile.getOriginalFilename());
            film.setUrlImg(fileName);
            this.filmService.salvaFilm(film);
            String uploadDir = "film-img/";
            FileUploadUtil.saveFile(uploadDir, fileName, multipartFile);
            model.addAttribute("films", this.filmService.getFilms());
            return "admin/films";
        }
        log.warn("Parametri inseriti non Validi");
        return "admin/filmForm";
    }

    @GetMapping("/films/{id}")
    public String mostraFilm(@PathVariable Long id, Model model) {
        log.info("Richiesta GET /films/" + id);
        Utente utente = this.userDetailsComponent.getUtenteAutenticato();
        Film film = this.filmService.getFilm(id);
        boolean esisteRecensione = this.recensioneService.esisteRecensione(utente, film);
        model.addAttribute("film", this.filmService.getFilm(id));
        model.addAttribute("esisteRecensione", esisteRecensione);
        return "film";
    }
    
}
